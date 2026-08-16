import httpx
from fastapi import APIRouter, HTTPException

from app.core.config import settings
from app.schemas.llm import LLMRequest, LLMResponse

router = APIRouter(prefix="/llm", tags=["llm"])


@router.post("/generate", response_model=LLMResponse)
async def generate(payload: LLMRequest):
    try:
        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(
                f"{settings.ollama_base_url}/api/generate",
                json={
                    "model": settings.ollama_model,
                    "prompt": payload.text,
                    "stream": False,
                },
            )
            resp.raise_for_status()
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=f"LLM request failed: {exc}") from exc

    data = resp.json()
    return LLMResponse(response=data.get("response", ""))
