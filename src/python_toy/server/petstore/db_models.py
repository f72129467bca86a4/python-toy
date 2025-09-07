from __future__ import annotations

from sqlalchemy import Integer, String, ForeignKey, DateTime, Enum, Text
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
import enum

from python_toy.server.petstore.id_type import PetId, CategoryId, TagId, UserId, OrderId


class Base(AsyncAttrs, DeclarativeBase):
    pass


class StatusEnum(enum.Enum):
    available = "available"
    pending = "pending"
    sold = "sold"


class PetEntity(Base):
    __tablename__ = "pets"

    id: Mapped[PetId] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    category_id: Mapped[CategoryId] = mapped_column(String(64), ForeignKey("categories.id"), nullable=True)
    status: Mapped[StatusEnum] = mapped_column(Enum(StatusEnum), default=StatusEnum.available)
    # Store as TEXT for compatibility; we'll encode/decode in the repository/mapper.
    photo_urls: Mapped[str] = mapped_column(Text, default="")
    owner_id: Mapped[UserId] = mapped_column(String(64), ForeignKey("users.id"), nullable=True)

    category: Mapped[CategoryEntity] = relationship("CategoryEntity", back_populates="pets")
    owner: Mapped[UserEntity] = relationship("UserEntity", back_populates="pets")
    tags: Mapped[list[TagEntity]] = relationship("TagEntity", secondary="pet_tags", back_populates="pets")


class CategoryEntity(Base):
    __tablename__ = "categories"

    id: Mapped[CategoryId] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)

    pets: Mapped[list[PetEntity]] = relationship("PetEntity", back_populates="category")


class TagEntity(Base):
    __tablename__ = "tags"

    id: Mapped[TagId] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)

    pets: Mapped[list[PetEntity]] = relationship("PetEntity", secondary="pet_tags", back_populates="tags")


class UserEntity(Base):
    __tablename__ = "users"

    id: Mapped[UserId] = mapped_column(String(64), primary_key=True)
    username: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str] = mapped_column(String(20), nullable=True)

    pets: Mapped[list[PetEntity]] = relationship("PetEntity", back_populates="owner")
    orders: Mapped[list[OrderEntity]] = relationship("OrderEntity", back_populates="user")


class OrderEntity(Base):
    __tablename__ = "orders"

    id: Mapped[OrderId] = mapped_column(String(64), primary_key=True)
    pet_id: Mapped[PetId] = mapped_column(String(64), ForeignKey("pets.id"), nullable=False)
    user_id: Mapped[UserId] = mapped_column(String(64), ForeignKey("users.id"), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, default=1)
    ship_date: Mapped[DateTime] = mapped_column(DateTime, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="placed")  # placed, approved, delivered
    complete: Mapped[bool] = mapped_column(default=False)

    pet: Mapped[PetEntity] = relationship("PetEntity")
    user: Mapped[UserEntity] = relationship("UserEntity", back_populates="orders")


# Association table for many-to-many relationship between Pet and Tag
class PetTagAssociation(Base):
    __tablename__ = "pet_tags"

    pet_id: Mapped[PetId] = mapped_column(String(64), ForeignKey("pets.id"), primary_key=True)
    tag_id: Mapped[TagId] = mapped_column(String(64), ForeignKey("tags.id"), primary_key=True)
