from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

Title = Annotated[str, Field(min_length=1, max_length=200)]
Skill = Annotated[str, Field(min_length=1, max_length=100)]


class PortfolioBase(BaseModel):
    title: Title
    description: str
    skills: list[Skill] = []


class PortfolioCreate(PortfolioBase):
    pass


class PortfolioUpdate(BaseModel):
    title: Title | None = None
    description: str | None = None
    skills: list[Skill] | None = None


class Portfolio(PortfolioBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
