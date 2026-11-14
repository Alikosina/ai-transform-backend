from typing import Annotated

from pydantic import AfterValidator, BaseModel, Field

from app.services.mail import is_valid_email


def _check_email(value: str) -> str:
    if not is_valid_email(value):
        raise ValueError("invalid email address")
    return value.strip()


Email = Annotated[str, Field(max_length=254), AfterValidator(_check_email)]


class UserRegister(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    surname: str = Field(min_length=1, max_length=100)
    email: Email
    password: str = Field(min_length=8, max_length=72)
    phone: str | None = Field(default=None, max_length=32)
    telegram: str | None = Field(default=None, max_length=64)


class UserLogin(BaseModel):
    email: Email
    password: str = Field(min_length=1, max_length=72)


class UserPublic(BaseModel):
    id: int
    name: str
    surname: str
    email: str
    phone: str | None = None
    telegram: str | None = None
    avatar: str | None = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserPublic
