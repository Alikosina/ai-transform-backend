from fastapi import APIRouter, HTTPException
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
import httpx

from app.core.config import settings
from app.schemas.llm import DraftRef, LLMRequest, LLMResponse
from app.services.drafts import create_draft, get_draft, remove_draft, try_reserve_send
from app.services.mail import MailError, is_valid_email, send_email
from app.services.rag import retrieve_context

router = APIRouter(prefix="/llm", tags=["llm"])

# How many previous exchanges (user message + assistant reply) to keep as context.
HISTORY_TURNS = 2

SYSTEM_PROMPT = (
    "Ты — AI помощник на портале asloyanportal.ru.\n"
    "ПРАВИЛА:\n"
    "- Отвечай ТОЛЬКО на русском языке, грамотно и естественно.\n"
    "- Не используй английские слова, кроме имён собственных и общепринятых "
    "технических терминов (Python, React, API).\n"
    "- Никогда не используй китайские, японские и другие нелатинские/некириллические символы.\n"
    "- Используй контекст, если он релевантен; иначе отвечай из общих знаний, "
    "не упоминая контекст.\n"
    "- Если пользователь просит отправить письмо, вызови инструмент send_email. "
    "Адрес получателя бери только из сообщения пользователя, не придумывай его.\n"
    "- Никогда не говори, что письмо уже отправлено: оно уйдёт только после подтверждения пользователем.\n\n"
    "<context>\n{context}\n</context>"
)

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", SYSTEM_PROMPT),
        MessagesPlaceholder("history", optional=True),
        ("human", "{text}\n\n(Ответь на русском языке.)"),
    ]
)

SEND_EMAIL_TOOL = {
    "type": "function",
    "function": {
        "name": "send_email",
        "description": (
            "Подготовить письмо на указанный адрес. Письмо НЕ отправляется сразу: "
            "пользователь увидит черновик и подтвердит отправку."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "to": {"type": "string", "description": "Email получателя из сообщения пользователя"},
                "subject": {"type": "string", "description": "Тема письма"},
                "body": {"type": "string", "description": "Текст письма"},
            },
            "required": ["to", "subject", "body"],
        },
    },
}


@router.post("/generate", response_model=LLMResponse)
async def generate(payload: LLMRequest):
    # Агент работает на GPT-5.6 Luna через AITunnel (OpenAI-совместимый API).
    # verify=False: TLS-проверка отключена (локальный прокси подменяет сертификат).
    llm = ChatOpenAI(
        api_key=settings.aitunnel_api_key.get_secret_value(),
        base_url=settings.aitunnel_base_url,
        model=settings.aitunnel_model,
        temperature=0.2,
        extra_body={"reasoning": {"effort": "medium"}},
        http_client=httpx.Client(verify=False),
        http_async_client=httpx.AsyncClient(verify=False),
    )
    chain = prompt | llm.bind_tools([SEND_EMAIL_TOOL])

    context = retrieve_context(payload.text) or "Контекст отсутствует."

    # Keep only the last HISTORY_TURNS exchanges, regardless of what the client sent.
    recent_history = payload.history[-HISTORY_TURNS * 2 :]
    history = [
        HumanMessage(content=message.content)
        if message.role == "user"
        else AIMessage(content=message.content)
        for message in recent_history
    ]

    try:
        result = await chain.ainvoke({"text": payload.text, "context": context, "history": history})
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"LLM request failed: {exc}") from exc

    for call in result.tool_calls:
        if call["name"] != "send_email":
            continue
        args = call["args"]
        to = str(args.get("to", ""))
        if not is_valid_email(to):
            return LLMResponse(
                response="Не удалось подготовить письмо: укажите корректный адрес получателя."
            )
        draft = create_draft(to, str(args.get("subject", "")), str(args.get("body", "")))
        return LLMResponse(
            response=result.content or "Черновик письма готов. Проверьте и подтвердите отправку.",
            draft=draft,
        )

    return LLMResponse(response=result.content)


@router.post("/email/confirm")
async def confirm_email(payload: DraftRef):
    draft = get_draft(payload.draft_id)
    if draft is None:
        raise HTTPException(status_code=404, detail="Черновик не найден или истёк")

    if not try_reserve_send():
        raise HTTPException(status_code=429, detail="Превышен лимит отправки писем, попробуйте позже")

    try:
        await send_email(draft.to, draft.subject, draft.body)
    except MailError as exc:
        # Draft is kept so the user can retry.
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    remove_draft(draft.draft_id)
    return {"status": "sent", "to": draft.to}


@router.post("/email/cancel")
async def cancel_email(payload: DraftRef):
    remove_draft(payload.draft_id)
    return {"status": "cancelled"}
