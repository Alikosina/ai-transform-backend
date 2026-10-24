from fastapi import APIRouter, HTTPException
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_ollama import ChatOllama

from app.core.config import settings
from app.schemas.llm import LLMRequest, LLMResponse
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
    "не упоминая контекст.\n\n"
    "<context>\n{context}\n</context>"
)

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", SYSTEM_PROMPT),
        MessagesPlaceholder("history", optional=True),
        ("human", "{text}\n\n(Ответь на русском языке.)"),
    ]
)


@router.post("/generate", response_model=LLMResponse)
async def generate(payload: LLMRequest):
    llm = ChatOllama(
        base_url=settings.ollama_base_url,
        model=settings.ollama_model,
        temperature=0.2,
        top_k=30,
        top_p=0.85,
        repeat_penalty=1.1,
        num_ctx=4096,
    )
    chain = prompt | llm

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

    return LLMResponse(response=result.content)
