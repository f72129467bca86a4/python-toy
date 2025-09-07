"""Query options for controlling eager loading behavior."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class PetQueryOptions:
    """Options for controlling Pet query behavior and eager loading."""

    include_category: bool = False
    include_owner: bool = False
    include_tags: bool = False
    include_all: bool = False

    def __post_init__(self) -> None:
        """If include_all is True, set all other options to True."""
        if self.include_all:
            self.include_category = True
            self.include_owner = True
            self.include_tags = True

    @classmethod
    def all(cls) -> PetQueryOptions:
        """Create options with all relations included."""
        return cls(include_all=True)

    @classmethod
    def minimal(cls) -> PetQueryOptions:
        """Create options with no relations included."""
        return cls()

    @classmethod
    def with_category(cls) -> PetQueryOptions:
        """Create options with only category included."""
        return cls(include_category=True)

    @classmethod
    def with_owner(cls) -> PetQueryOptions:
        """Create options with only owner included."""
        return cls(include_owner=True)

    @classmethod
    def with_tags(cls) -> PetQueryOptions:
        """Create options with only tags included."""
        return cls(include_tags=True)


@dataclass
class CategoryQueryOptions:
    """Options for controlling Category query behavior."""

    include_pets: bool = False

    @classmethod
    def minimal(cls) -> CategoryQueryOptions:
        """Create options with no relations included."""
        return cls()

    @classmethod
    def with_pets(cls) -> CategoryQueryOptions:
        """Create options with pets included."""
        return cls(include_pets=True)


@dataclass
class UserQueryOptions:
    """Options for controlling User query behavior."""

    include_pets: bool = False
    include_orders: bool = False

    @classmethod
    def minimal(cls) -> UserQueryOptions:
        """Create options with no relations included."""
        return cls()

    @classmethod
    def with_pets(cls) -> UserQueryOptions:
        """Create options with pets included."""
        return cls(include_pets=True)

    @classmethod
    def with_orders(cls) -> UserQueryOptions:
        """Create options with orders included."""
        return cls(include_orders=True)

    @classmethod
    def with_all_relations(cls) -> UserQueryOptions:
        """Create options with all relations included."""
        return cls(include_pets=True, include_orders=True)


__all__ = ("PetQueryOptions", "CategoryQueryOptions", "UserQueryOptions")
