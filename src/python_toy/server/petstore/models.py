from __future__ import annotations


from pydantic import BaseModel, Field
from pydantic.experimental.missing_sentinel import MISSING

from python_toy.server.petstore.id_type import PetId, CategoryId, TagId, UserId, OrderId


class Pet(BaseModel):
    """Pet domain model."""

    id: PetId
    name: str = Field(min_length=1, max_length=100)
    category: Category | None = None
    status: str = Field(default="available", pattern=r"^(available|pending|sold)$")
    photo_urls: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)  # Tag names for API compatibility
    owner: User | None = None


class Category(BaseModel):
    """Category domain model."""

    id: CategoryId
    name: str = Field(min_length=1, max_length=100)


class Tag(BaseModel):
    """Tag domain model."""

    id: TagId
    name: str = Field(min_length=1, max_length=100)


class User(BaseModel):
    """User domain model."""

    id: UserId
    username: str = Field(min_length=1, max_length=100)
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    email: str = Field(min_length=1, max_length=100)
    phone: str | None = None


class Order(BaseModel):
    """Order domain model."""

    id: OrderId
    pet_id: PetId
    user_id: UserId
    quantity: int = Field(default=1, ge=1)
    ship_date: str | None = None  # ISO format
    status: str = Field(default="placed", pattern=r"^(placed|approved|delivered)$")
    complete: bool = False


class PetCreate(BaseModel):
    """Pet creation payload."""

    name: str = Field(min_length=1, max_length=100, examples=["야옹이"])
    category_id: CategoryId | None = None
    status: str = Field(default="available", pattern=r"^(available|pending|sold)$", examples=["available"])
    photo_urls: list[str] = Field(default_factory=list, examples=[["http://example.com/photo1.jpg"]])
    tags: list[str] = Field(default_factory=list, examples=[["dog", "cute"]])
    owner_id: UserId | None = None


class PetUpdate(BaseModel):
    """Pet update payload with optional fields."""

    name: str | MISSING = Field(default=MISSING, min_length=1, max_length=100)  # type: ignore[valid-type]
    category_id: CategoryId | None | MISSING = MISSING  # type: ignore[valid-type]
    status: str | MISSING = Field(default=MISSING, pattern=r"^(available|pending|sold)$")  # type: ignore[valid-type]
    photo_urls: list[str] | MISSING = MISSING  # type: ignore[valid-type]
    tags: list[str] | MISSING = MISSING  # type: ignore[valid-type]
    owner_id: UserId | None | MISSING = MISSING  # type: ignore[valid-type]


class CategoryCreate(BaseModel):
    """Category creation payload."""

    name: str = Field(min_length=1, max_length=100)


class TagCreate(BaseModel):
    """Tag creation payload."""

    name: str = Field(min_length=1, max_length=100)


class UserCreate(BaseModel):
    """User creation payload."""

    username: str = Field(min_length=1, max_length=100)
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    email: str = Field(min_length=1, max_length=100)
    password: str = Field(min_length=8, max_length=255)
    phone: str | None = None


class OrderCreate(BaseModel):
    """Order creation payload."""

    pet_id: PetId
    user_id: UserId
    quantity: int = Field(default=1, ge=1)
    ship_date: str | None = None


__all__ = (
    "Pet",
    "Category",
    "Tag",
    "User",
    "Order",
    "PetCreate",
    "PetUpdate",
    "CategoryCreate",
    "TagCreate",
    "UserCreate",
    "OrderCreate",
)
