from typing import Annotated

from pydantic import BaseModel, Field, ConfigDict


class EmptyResponse(BaseModel):
    model_config = ConfigDict(frozen=True)


class ListResponse[T](BaseModel):
    model_config = ConfigDict(frozen=True)

    items: list[Annotated[T, Field(...)]]

    @staticmethod
    def empty() -> "ListResponse[T]":
        return ListResponse(items=[])

    @staticmethod
    def of(items: list[T]) -> "ListResponse[T]":
        if not items:
            return ListResponse.empty()
        return ListResponse(items=items)


class PageResponse[T](ListResponse[T]):
    model_config = ConfigDict(frozen=True)

    total: int
    page: int
    size: int

    @classmethod
    def create(cls, items: list[T], total: int, page: int, size: int) -> "PageResponse[T]":
        return cls(items=items, total=total, page=page, size=size)


__all__ = ["EmptyResponse", "ListResponse", "PageResponse"]
