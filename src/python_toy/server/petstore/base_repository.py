from __future__ import annotations

from abc import ABC, abstractmethod
import re
from typing import TypeVar

from pydantic import BaseModel
from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from python_toy.server.infra.error import (
    BadRequestException,
    DuplicateEntityException,
    EntityNotFoundException,
    ForeignKeyViolationException,
)

T = TypeVar("T", bound=BaseModel)
TCreate = TypeVar("TCreate", bound=BaseModel)
TDB = TypeVar("TDB")


class BaseRepository[T, TCreate, TDB](ABC):
    """Base repository with common CRUD operations."""

    def __init__(self, session: AsyncSession, db_model: type[TDB]) -> None:
        self.session = session
        self.db_model = db_model
        self.entity_type = db_model.__name__

    async def ensure_foreign_key_exists(self, table: type, id_value: str, field_name: str) -> None:
        """Validate that a foreign key reference exists.

        Args:
            table: The target table/model class
            id_value: The ID value to check
            field_name: Field name for error message

        Raises:
            ForeignKeyViolationException: If the foreign key doesn't exist
        """
        if id_value is None:
            return  # nullable FK is allowed

        stmt = select(table.id).where(table.id == id_value)  # type: ignore[attr-defined]
        exists = (await self.session.execute(stmt)).scalar_one_or_none()
        if not exists:
            referenced_entity = table.__name__
            raise ForeignKeyViolationException(field_name, id_value, referenced_entity)

    def _analyze_integrity_error(self, error: IntegrityError, entity_type: str) -> Exception:
        """Analyze SQLite integrity error and return appropriate domain exception.

        Args:
            error: The IntegrityError from SQLAlchemy
            entity_type: The type of entity being processed

        Returns:
            Appropriate domain exception
        """
        error_msg = str(error.orig)

        # SQLite UNIQUE constraint violations
        if "UNIQUE constraint failed" in error_msg:
            # Extract field name from error message
            # Example: "UNIQUE constraint failed: users.email"
            match = re.search(r"UNIQUE constraint failed: \w+\.(\w+)", error_msg)
            field = match.group(1) if match else "field"
            return DuplicateEntityException(entity_type, field, "unknown_value")

        # SQLite FOREIGN KEY constraint violations
        if "FOREIGN KEY constraint failed" in error_msg:
            return ForeignKeyViolationException("foreign_key", "unknown_value")

        # Fallback to generic BadRequestException
        return BadRequestException(f"Database constraint violation: {error_msg}")

    def _to_domain(self, db_entity: TDB) -> T:
        """Convert DB entity to domain model. Legacy method - use Service layer instead."""
        msg = "Domain conversion should be handled by Service layer, not Repository"
        raise NotImplementedError(msg)

    @abstractmethod
    def _create_db_entity(self, payload: TCreate) -> TDB:
        """Create DB entity from create payload."""
        ...

    async def create_db_entity(self, payload: TCreate) -> TDB:
        """Create a new entity and return DB entity."""
        db_entity = self._create_db_entity(payload)
        self.session.add(db_entity)
        try:
            await self.session.flush()  # Flush within transaction context
            # Return DB entity (ID is available after flush)
        except IntegrityError as e:
            # Let Service level handle rollback
            domain_exception = self._analyze_integrity_error(e, self.entity_type)
            raise domain_exception from e
        return db_entity

    async def get_optional(self, entity_id: str) -> TDB | None:
        """Get DB entity by ID. Returns None if not found."""
        stmt = select(self.db_model).where(self.db_model.id == entity_id)  # type: ignore
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_required(self, entity_id: str) -> TDB:
        """Get DB entity by ID. Raises EntityNotFoundException if not found."""
        entity = await self.get_optional(entity_id)
        if entity is None:
            raise EntityNotFoundException(entity_type=self.entity_type, entity_id=entity_id)
        return entity

    async def delete(self, entity_id: str) -> None:
        """Delete entity by ID."""
        stmt = delete(self.db_model).where(self.db_model.id == entity_id)  # type: ignore
        result = await self.session.execute(stmt)
        if result.rowcount == 0:
            raise EntityNotFoundException(entity_type=self.entity_type, entity_id=entity_id)
        # Note: Transaction commit is handled at Service level


__all__ = ("BaseRepository",)
