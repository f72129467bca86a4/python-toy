from __future__ import annotations

from typing import Annotated

from pydantic import BaseModel, Field
from pydantic.experimental.missing_sentinel import MISSING


type PetId = Annotated[str, Field(min_length=1, max_length=64, pattern=r"^[a-zA-Z0-9]+$")]


class Pet(BaseModel):
    id: PetId
    name: str = Field(min_length=1, max_length=100)
    tags: list[str] = Field(default_factory=list)


class PetCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100, examples=["야옹이"])
    tags: list[str] = Field(default_factory=list, examples=[["cat", "cute"]])


class PetUpdate(BaseModel):
    name: str | MISSING = Field(default=MISSING, min_length=1, max_length=100)  # type: ignore[valid-type]
    tags: list[str] | MISSING = MISSING  # type: ignore[valid-type]


__all__ = ("PetId", "Pet", "PetCreate", "PetUpdate")
