"""Type aliases for the application."""

from __future__ import annotations
from pydantic import Field
from typing import Annotated

# Type aliases for entity IDs
# FYI: Dont assume UUID
type PetId = Annotated[str, Field(min_length=1, max_length=64, pattern=r"^[a-zA-Z0-9_-]+$")]
type CategoryId = Annotated[str, Field(min_length=1, max_length=64, pattern=r"^[a-zA-Z0-9_-]+$")]
type TagId = Annotated[str, Field(min_length=1, max_length=64, pattern=r"^[a-zA-Z0-9_-]+$")]
type UserId = Annotated[str, Field(min_length=1, max_length=64, pattern=r"^[a-zA-Z0-9_-]+$")]
type OrderId = Annotated[str, Field(min_length=1, max_length=64, pattern=r"^[a-zA-Z0-9_-]+$")]


__all__ = ("PetId", "CategoryId", "TagId", "UserId", "OrderId")
