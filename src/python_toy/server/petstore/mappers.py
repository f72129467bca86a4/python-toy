"""Central model mappers for Domain ↔ DB ↔ API conversions.

This module centralizes all model conversion logic, similar to Java's MapStruct pattern.
Each mapper handles conversions for a specific domain entity.
"""

from __future__ import annotations

from .models import Pet, Category, User, Tag
from .db_models import PetEntity, CategoryEntity, UserEntity, TagEntity


class PetMapper:
    """Mapper for Pet domain model conversions."""

    @staticmethod
    def to_domain(pet_db: PetEntity) -> Pet:
        """Convert PetEntity to Pet domain model with all relations.

        Args:
            pet_db: Database entity with relations loaded

        Returns:
            Pet domain model with all relations resolved
        """
        # Convert related entities using their respective mappers
        category = None
        if pet_db.category:
            category = CategoryMapper.to_domain(pet_db.category)

        owner = None
        if pet_db.owner:
            owner = UserMapper.to_domain(pet_db.owner)

        # Extract tag names from the relationship, sorted to maintain consistency
        # Handle both eagerly loaded and lazy loaded tags
        try:
            tag_names = sorted([tag.name for tag in pet_db.tags]) if pet_db.tags else []
        except Exception:
            # If tags are not loaded (lazy loading), return empty list
            tag_names = []

        # photo_urls stored as TEXT; support JSON array string, comma-delimited, or empty
        photo_urls_raw = getattr(pet_db, "photo_urls", "") or ""
        photo_urls: list[str]
        if isinstance(photo_urls_raw, list):
            photo_urls = list(photo_urls_raw)
        else:
            try:
                import json

                parsed = json.loads(photo_urls_raw) if photo_urls_raw else []
                photo_urls = list(parsed) if isinstance(parsed, list) else []
            except Exception:
                photo_urls = [p for p in (photo_urls_raw.split(",") if photo_urls_raw else []) if p]

        return Pet(
            id=pet_db.id,
            name=pet_db.name,
            category=category,
            status=pet_db.status.value if hasattr(pet_db.status, "value") else str(pet_db.status),
            photo_urls=photo_urls,
            tags=tag_names,
            owner=owner,
        )


class CategoryMapper:
    """Mapper for Category domain model conversions."""

    @staticmethod
    def to_domain(category_db: CategoryEntity) -> Category:
        """Convert Category to Category domain model."""
        return Category(
            id=category_db.id,
            name=category_db.name,
        )


class UserMapper:
    """Mapper for User domain model conversions."""

    @staticmethod
    def to_domain(user_db: UserEntity) -> User:
        """Convert UserEntity to User domain model."""
        return User(
            id=user_db.id,
            username=user_db.username,
            first_name=user_db.first_name,
            last_name=user_db.last_name,
            email=user_db.email,
            phone=user_db.phone,
        )


class TagMapper:
    """Mapper for Tag domain model conversions."""

    @staticmethod
    def to_domain(tag_db: TagEntity) -> Tag:
        """Convert TagEntity to Tag domain model."""
        return Tag(
            id=tag_db.id,
            name=tag_db.name,
        )


__all__ = (
    "PetMapper",
    "CategoryMapper",
    "UserMapper",
    "TagMapper",
)
