###Pydantic models are Python classes that define the shape of your data and validate it automatically.
###For kontexus, the Context model describes what a context entry is — every field, its type, and whether
###it's required or optional.

"""Data models and enums shared across CLI and API."""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class Tier(str, Enum):
    S = "S"
    A = "A"
    B = "B"
    F = "F"


class ContextCreate(BaseModel):
    prompt: str = Field(..., min_length=1)
    summary: str = Field(..., min_length=1)
    source_chat: Optional[str] = None
    llm_used: str = Field(..., min_length=1)
    tier: Optional[Tier] = None
    comment: Optional[str] = None


class Context(ContextCreate):
    id: int
    created: datetime

