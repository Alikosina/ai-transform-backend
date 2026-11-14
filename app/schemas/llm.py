from typing import Literal

from pydantic import BaseModel


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class LLMRequest(BaseModel):
    text: str
    history: list[ChatMessage] = []


class EmailDraft(BaseModel):
    draft_id: str
    to: str
    subject: str
    body: str


class LLMResponse(BaseModel):
    response: str
    draft: EmailDraft | None = None


class DraftRef(BaseModel):
    draft_id: str
