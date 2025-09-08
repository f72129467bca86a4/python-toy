from __future__ import annotations

import uuid

from sqlalchemy import delete, func, select

from python_toy.server.infra.error import EntityNotFoundException
from python_toy.server.petstore.db_models import CategoryEntity
from .models import CategoryCreate
from .base_repository import BaseRepository, SessionSupplier


class CategoryRepository(BaseRepository[CategoryEntity, CategoryCreate, CategoryEntity]):
    def __init__(self, session_supplier: SessionSupplier) -> None:
        super().__init__(CategoryEntity, session_supplier)

    def _create_db_entity(self, payload: CategoryCreate) -> CategoryEntity:
        return CategoryEntity(id=str(uuid.uuid4()), name=payload.name)

    async def create(self, payload: CategoryCreate) -> CategoryEntity:
        """Create a new category."""
        return await self.create_db_entity(payload)

    async def list(self, *, page: int = 1, size: int = 10) -> tuple[list[CategoryEntity], int]:
        """List Category entities ordered by name."""
        total = int((await self.session.execute(select(func.count()).select_from(CategoryEntity))).scalar_one())

        q = select(CategoryEntity).order_by(CategoryEntity.name).offset((page - 1) * size).limit(size)
        items = (await self.session.execute(q)).scalars().all()
        return list(items), total

    async def get(self, entity_id: str) -> CategoryEntity:
        return await self.get_required(entity_id)

    async def delete(self, entity_id: str) -> None:
        res = await self.session.execute(delete(CategoryEntity).where(CategoryEntity.id == entity_id))
        if res.rowcount == 0:
            raise EntityNotFoundException(entity_type="Category", entity_id=entity_id)


__all__ = ("CategoryRepository",)
