from __future__ import annotations

import uuid
from typing import cast, List
import json

from sqlalchemy import select, update, delete, func
from sqlalchemy.orm import selectinload

from python_toy.server.infra.error import EntityNotFoundException
from .models import PetCreate, PetUpdate
from pydantic.experimental.missing_sentinel import MISSING
from python_toy.server.petstore.db_models import CategoryEntity, PetEntity, UserEntity, PetTagAssociation
from .base_repository import BaseRepository, SessionSupplier
from .query_options import PetQueryOptions

from python_toy.server.petstore.id_type import PetId, CategoryId, UserId


class DBPetRepository(BaseRepository[PetEntity, PetCreate, PetEntity]):
    def __init__(self, session_supplier: SessionSupplier) -> None:
        super().__init__(PetEntity, session_supplier)

    def _create_db_entity(self, payload: PetCreate) -> PetEntity:
        return PetEntity(
            id=str(uuid.uuid4()),
            name=payload.name,
            category_id=payload.category_id,
            status=payload.status,
            photo_urls=json.dumps(list(payload.photo_urls or [])),
            owner_id=payload.owner_id,
        )

    async def create(self, payload: PetCreate, tag_ids: list[str] | None = None) -> PetEntity:
        # Validate FKs if provided using base class helper
        if payload.category_id is not None:
            await self.ensure_foreign_key_exists(CategoryEntity, payload.category_id, "category_id")
        if payload.owner_id is not None:
            await self.ensure_foreign_key_exists(UserEntity, payload.owner_id, "owner_id")

        # Create base entity using parent method
        pet_db = await self.create_db_entity(payload)

        # Add tags association
        if tag_ids:
            for tag_id in tag_ids:
                assoc = PetTagAssociation(pet_id=pet_db.id, tag_id=tag_id)
                self.session.add(assoc)

        # Return DB entity only - domain conversion is Service responsibility
        return pet_db

    async def list_db_entities(
        self, *, page: int | None = None, size: int | None = None
    ) -> tuple[list[PetEntity], int]:
        """List Pet entities without relations - for Service layer processing."""
        total_stmt = select(func.count()).select_from(PetEntity)
        total = (await self.session.execute(total_stmt)).scalar_one()

        stmt = select(PetEntity).order_by(PetEntity.id)
        if page is not None and size is not None:
            offset = (page - 1) * size
            stmt = stmt.offset(offset).limit(size)

        result = await self.session.execute(stmt)
        pets_db = list(result.scalars().all())
        return pets_db, total

    async def get_with_relations(self, entity_id: PetId) -> PetEntity:
        """Get Pet with all relations eagerly loaded."""
        return await self.get_with_options(entity_id, PetQueryOptions.all())

    async def get_with_options(self, entity_id: PetId, options: PetQueryOptions) -> PetEntity:
        """Get Pet with selective relation loading based on options."""
        stmt = select(PetEntity).where(PetEntity.id == entity_id)

        # Apply selective eager loading based on options
        load_options = []
        if options.include_category:
            load_options.append(selectinload(PetEntity.category))
        if options.include_owner:
            load_options.append(selectinload(PetEntity.owner))
        if options.include_tags:
            load_options.append(selectinload(PetEntity.tags))

        if load_options:
            stmt = stmt.options(*load_options)

        result = await self.session.execute(stmt)
        pet_db = result.scalar_one_or_none()
        if not pet_db:
            raise EntityNotFoundException(entity_type="Pet", entity_id=entity_id)
        return pet_db

    async def list_with_relations(
        self, *, page: int | None = None, size: int | None = None
    ) -> tuple[list[PetEntity], int]:
        """List DB entities with all relations eagerly loaded."""
        return await self.list_with_options(page=page, size=size, options=PetQueryOptions.all())

    async def list_with_options(
        self,
        *,
        page: int | None = None,
        size: int | None = None,
        options: PetQueryOptions,
    ) -> tuple[list[PetEntity], int]:
        """List DB entities with selective relation loading based on options."""
        total_stmt = select(func.count()).select_from(PetEntity)
        total = (await self.session.execute(total_stmt)).scalar_one()

        stmt = select(PetEntity).order_by(PetEntity.id)

        # Apply selective eager loading based on options
        load_options = []
        if options.include_category:
            load_options.append(selectinload(PetEntity.category))
        if options.include_owner:
            load_options.append(selectinload(PetEntity.owner))
        if options.include_tags:
            load_options.append(selectinload(PetEntity.tags))

        if load_options:
            stmt = stmt.options(*load_options)
        if page is not None and size is not None:
            offset = (page - 1) * size
            stmt = stmt.offset(offset).limit(size)

        result = await self.session.execute(stmt)
        pets_db = list(result.scalars().all())
        return pets_db, total

    async def patch(self, entity_id: PetId, payload: PetUpdate, tag_ids: List[str] | None = None) -> PetEntity:  # noqa: UP006
        update_data: dict[str, object] = {}
        if payload.name is not MISSING:  # type: ignore[comparison-overlap]
            update_data["name"] = payload.name
        if payload.category_id is not MISSING:  # type: ignore[comparison-overlap]
            if payload.category_id is not None:
                await self.ensure_foreign_key_exists(CategoryEntity, payload.category_id, "category_id")
            update_data["category_id"] = cast(CategoryId, payload.category_id)
        if payload.status is not MISSING:  # type: ignore[comparison-overlap]
            update_data["status"] = payload.status
        if payload.photo_urls is not MISSING:  # type: ignore[comparison-overlap]
            update_data["photo_urls"] = json.dumps(list(payload.photo_urls or []))
        if payload.owner_id is not MISSING:  # type: ignore[comparison-overlap]
            if payload.owner_id is not None:
                await self.ensure_foreign_key_exists(UserEntity, payload.owner_id, "owner_id")
            update_data["owner_id"] = cast(UserId, payload.owner_id)

        if update_data:
            stmt = update(PetEntity).where(PetEntity.id == entity_id).values(**update_data)
            await self.session.execute(stmt)

        if payload.tags is not MISSING:  # type: ignore[comparison-overlap]
            # Delete existing associations
            delete_stmt = delete(PetTagAssociation).where(PetTagAssociation.pet_id == entity_id)
            await self.session.execute(delete_stmt)
            # Re-create associations
            if tag_ids:
                for tag_id in tag_ids:
                    assoc = PetTagAssociation(pet_id=entity_id, tag_id=tag_id)
                    self.session.add(assoc)

        # Note: Transaction commit is handled at Service level
        await self.session.flush()  # Ensure changes are persisted within transaction
        return await self.get_required(entity_id)

    async def delete(self, entity_id: PetId) -> None:
        # Remove tag associations first
        stmt = delete(PetTagAssociation).where(PetTagAssociation.pet_id == entity_id)
        await self.session.execute(stmt)
        stmt = delete(PetEntity).where(PetEntity.id == entity_id)
        result = await self.session.execute(stmt)
        if result.rowcount == 0:
            raise EntityNotFoundException(entity_type="Pet", entity_id=entity_id)
        # Note: Transaction commit is handled at Service level

    async def get_db_entity(self, entity_id: PetId) -> PetEntity:
        """Get DB entity without relations - for Service layer processing."""
        return await self.get_required(entity_id)


__all__ = ("DBPetRepository",)
