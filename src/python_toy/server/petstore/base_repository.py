from __future__ import annotations

import re
from typing import Callable, Any, Protocol

from sqlalchemy import delete, select, ForeignKey
from sqlalchemy.orm import QueryableAttribute
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from python_toy.server.petstore.db_models import Base as ORMBase

from python_toy.server.infra.error import (
    BadRequestException,
    DuplicateEntityException,
    EntityNotFoundException,
    ForeignKeyViolationException,
)

# Session supplier type (like Java's Supplier<AsyncSession>)
SessionSupplier = Callable[[], AsyncSession]


class BaseRepository[EntityT]:
    """Base repository with common CRUD operations."""

    def __init__(self, db_model: type[EntityT], session_supplier: SessionSupplier) -> None:
        self.db_model = db_model
        self.entity_type = db_model.__name__
        self._session_supplier = session_supplier

    @property
    def _session(self) -> AsyncSession:
        """Get the current database session from supplier."""
        return self._session_supplier()

    async def ensure_foreign_key_exists(self, column: QueryableAttribute[Any], fk_value: object) -> None:
        """
        Ensure referenced foreign key exists.

        :param column: A mapped_column
        :param fk_value: FK value to check

        :raises ForeignKeyViolationException: When the foreign key does not exist
        """
        if fk_value is None:
            return

        try:
            fk: ForeignKey = next(iter(column.foreign_keys))
        except (StopIteration, AttributeError):
            msg = f"Foreign key not defined on column '{column.key}'"
            raise BadRequestException(msg) from None

        ref_column = fk.column
        stmt = select(ref_column).where(ref_column == fk_value)
        result = await self._session.execute(stmt)
        if not result.scalar_one_or_none():
            referenced_entity = self._resolve_entity_name_from_column(ref_column)
            raise ForeignKeyViolationException(
                field=column.key, value=str(fk_value), referenced_entity=referenced_entity
            )

    @staticmethod
    def _resolve_entity_name_from_column(column: _HasTable) -> str:
        try:
            table = column.table
        except Exception:
            return str(column)

        # Find from SQLAlchemy Declarative registry, reverse lookup from Table to Mapper
        for mapper in ORMBase.registry.mappers:
            mapped_table = getattr(mapper, "persist_selectable", None)
            if mapped_table is None:
                mapped_table = getattr(mapper, "local_table", None)
            if mapped_table is None:
                mapped_table = getattr(mapper, "mapped_table", None)
            if mapped_table is table:
                return mapper.class_.__name__

        # Fallback: Retrieve table name and format it
        name = getattr(table, "name", str(table))
        return name.capitalize() + "Entity"

    def _analyze_integrity_error(self, error: IntegrityError, entity_type: str) -> Exception:
        """Analyze SQLite integrity error and return appropriate domain exception.

        :param error: The IntegrityError from SQLAlchemy
        :param entity_type: The type of entity being processed

        :return: Appropriate domain exception
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

    async def create(self, entity: EntityT) -> EntityT:
        """Create a new entity and return DB entity."""
        self._session.add(entity)
        try:
            await self._session.flush()  # Flush within transaction context
            # Return DB entity (ID is available after flush)
        except IntegrityError as e:
            # Let Service level handle rollback
            domain_exception = self._analyze_integrity_error(e, self.entity_type)
            raise domain_exception from e
        return entity

    async def get_optional(self, entity_id: str) -> EntityT | None:
        """Get DB entity by ID. Returns None if not found."""
        stmt = select(self.db_model).where(self.db_model.id == entity_id)  # type: ignore
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_required(self, entity_id: str) -> EntityT:
        """Get DB entity by ID. Raises EntityNotFoundException if not found."""
        if (entity := await self.get_optional(entity_id)) is None:
            raise EntityNotFoundException(entity_type=self.entity_type, entity_id=entity_id)
        return entity

    async def delete(self, entity_id: str) -> None:
        stmt = delete(self.db_model).where(self.db_model.id == entity_id)  # type: ignore
        result = await self._session.execute(stmt)
        if result.rowcount == 0:
            raise EntityNotFoundException(entity_type=self.entity_type, entity_id=entity_id)
        # Note: Transaction commit is handled at Service level


class _HasTable(Protocol):
    table: Any


__all__ = ("BaseRepository",)
