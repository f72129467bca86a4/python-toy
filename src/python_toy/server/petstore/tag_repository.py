from __future__ import annotations

import uuid
from typing import Iterable, List

from sqlalchemy import func, select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from python_toy.server.infra.error import EntityNotFoundException, DuplicateEntityException
from python_toy.server.petstore.db_models import TagEntity
from .models import TagCreate
from .base_repository import BaseRepository


class TagRepository(BaseRepository[TagEntity, TagCreate, TagEntity]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, TagEntity)

    def _create_db_entity(self, payload: TagCreate) -> TagEntity:
        return TagEntity(id=str(uuid.uuid4()), name=payload.name)

    async def create(self, payload: TagCreate) -> TagEntity:
        """Create a new tag."""
        try:
            return await self.create_db_entity(payload)
        except DuplicateEntityException:
            # propagate domain-specific duplicate
            raise

    async def list(self, *, page: int = 1, size: int = 10) -> tuple[list[TagEntity], int]:
        """List Tag entities ordered by name."""
        total = int((await self.session.execute(select(func.count()).select_from(TagEntity))).scalar_one())

        q = select(TagEntity).order_by(TagEntity.name).offset((page - 1) * size).limit(size)
        items = (await self.session.execute(q)).scalars().all()
        return list(items), total

    async def get(self, entity_id: str) -> TagEntity:
        return await self.get_required(entity_id)

    async def delete(self, entity_id: str) -> None:
        """Delete a tag by ID."""
        res = await self.session.execute(delete(TagEntity).where(TagEntity.id == entity_id))
        if res.rowcount == 0:
            raise EntityNotFoundException(entity_type="Tag", entity_id=entity_id)

    async def ensure_exist_by_names(self, names: Iterable[str]) -> List[TagEntity]:  # noqa: UP006
        """Ensure tags exist by names, creating if necessary."""
        existing_stmt = select(TagEntity).where(TagEntity.name.in_(list(names)))
        existing = (await self.session.execute(existing_stmt)).scalars().all()
        existing_map = {e.name: e for e in existing}
        created: list[TagEntity] = []
        for name in names:
            if name in existing_map:
                continue
            tag = TagEntity(id=str(uuid.uuid4()), name=name)
            self.session.add(tag)
            created.append(tag)
        if created:
            await self.session.flush()
        return list(existing_map.values()) + created


__all__ = ("TagRepository",)
