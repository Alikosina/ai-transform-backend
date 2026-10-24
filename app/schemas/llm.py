from typing import Literal

from pydantic import BaseModel


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class LLMRequest(BaseModel):
    text: str
    history: list[ChatMessage] = []


class LLMResponse(BaseModel):
    response: str
