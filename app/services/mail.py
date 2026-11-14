import asyncio
import re
import smtplib
import ssl
from email.message import EmailMessage

from app.core.config import settings

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class MailError(Exception):
    """Raised when an email cannot be sent."""


def is_valid_email(address: str) -> bool:
    return bool(EMAIL_RE.match(address.strip()))


def _send_sync(to: str, subject: str, body: str) -> None:
    if not is_valid_email(to):
        raise MailError(f"Некорректный адрес: {to!r}")
    if not settings.smtp_user or not settings.smtp_password.get_secret_value():
        raise MailError("SMTP не настроен: заполните SMTP_USER и SMTP_PASSWORD")

    message = EmailMessage()
    message["From"] = settings.smtp_user
    message["To"] = to.strip()
    message["Subject"] = subject
    message.set_content(body)

    context = ssl.create_default_context()
    try:
        if settings.smtp_port == 465:
            server = smtplib.SMTP_SSL(settings.smtp_host, settings.smtp_port, context=context, timeout=30)
        else:
            server = smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=30)
            server.starttls(context=context)
        with server:
            server.login(settings.smtp_user, settings.smtp_password.get_secret_value())
            server.send_message(message)
    except (smtplib.SMTPException, OSError) as exc:
        raise MailError(f"Не удалось отправить письмо: {exc}") from exc


async def send_email(to: str, subject: str, body: str) -> None:
    """Send a plain-text email via SMTP without blocking the event loop."""
    await asyncio.to_thread(_send_sync, to, subject, body)
