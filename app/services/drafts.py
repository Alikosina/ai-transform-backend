import time
import uuid
from collections import deque

from app.schemas.llm import EmailDraft

# Unconfirmed drafts expire after this many seconds.
DRAFT_TTL_SECONDS = 15 * 60
# Maximum number of emails the agent may send within the window.
SEND_LIMIT = 5
SEND_WINDOW_SECONDS = 60 * 60

_drafts: dict[str, tuple[float, EmailDraft]] = {}
_sent_at: deque[float] = deque()


def _purge_expired() -> None:
    now = time.monotonic()
    for draft_id, (expires_at, _) in list(_drafts.items()):
        if expires_at < now:
            del _drafts[draft_id]


def create_draft(to: str, subject: str, body: str) -> EmailDraft:
    _purge_expired()
    draft = EmailDraft(draft_id=uuid.uuid4().hex, to=to.strip(), subject=subject, body=body)
    _drafts[draft.draft_id] = (time.monotonic() + DRAFT_TTL_SECONDS, draft)
    return draft


def get_draft(draft_id: str) -> EmailDraft | None:
    _purge_expired()
    entry = _drafts.get(draft_id)
    return entry[1] if entry else None


def remove_draft(draft_id: str) -> None:
    _drafts.pop(draft_id, None)


def try_reserve_send() -> bool:
    """Return True and record a send if the hourly limit allows it."""
    now = time.monotonic()
    while _sent_at and _sent_at[0] < now - SEND_WINDOW_SECONDS:
        _sent_at.popleft()
    if len(_sent_at) >= SEND_LIMIT:
        return False
    _sent_at.append(now)
    return True
