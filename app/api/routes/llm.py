from fastapi import APIRouter, HTTPException
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama

from app.core.config import settings
from app.schemas.llm import LLMRequest, LLMResponse
from app.services.rag import retrieve_context

router = APIRouter(prefix="/llm", tags=["llm"])

SYSTEM_PROMPT = (
    "Ты — AI помощник на портале asloyanportal.ru. "
    "Используй приведённый ниже контекст, если он релевантен вопросу пользователя. "
    "Если контекст не относится к вопросу, отвечай на основе своих общих знаний, "
    "не упоминая, что контекст был нерелевантен.\n\n"
    "Контекст:\n{context}"
)

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", SYSTEM_PROMPT),
        ("human", "{text}"),
    ]
)


@router.post("/generate", response_model=LLMResponse)
async def generate(payload: LLMRequest):
    llm = ChatOllama(base_url=settings.ollama_base_url, model=settings.ollama_model)
    chain = prompt | llm

    context = retrieve_context(payload.text) or "Контекст отсутствует."

    try:
        result = await chain.ainvoke({"text": payload.text, "context": context})
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"LLM request failed: {exc}") from exc

    return LLMResponse(response=result.content)
