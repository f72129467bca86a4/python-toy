from __future__ import annotations

import uuid
from typing import Iterable, List

from sqlalchemy import func, select, delete

from python_toy.server.infra.error import EntityNotFoundException
from python_toy.server.petstore.db_models import TagEntity
from .base_repository import BaseRepository, SessionSupplier


class TagRepository(BaseRepository[TagEntity]):
    def __init__(self, session_supplier: SessionSupplier) -> None:
        super().__init__(TagEntity, session_supplier)

    async def list(self, *, page: int = 1, size: int = 10) -> tuple[list[TagEntity], int]:
        total = int((await self._session.execute(select(func.count()).select_from(TagEntity))).scalar_one())

        q = select(TagEntity).order_by(TagEntity.name).offset((page - 1) * size).limit(size)
        items = (await self._session.execute(q)).scalars().all()
        return list(items), total

    async def get(self, entity_id: str) -> TagEntity:
        return await self.get_required(entity_id)

    async def delete(self, entity_id: str) -> None:
        res = await self._session.execute(delete(TagEntity).where(TagEntity.id == entity_id))
        if res.rowcount == 0:
            raise EntityNotFoundException(entity_type=self.entity_type, entity_id=entity_id)

    async def ensure_exist_by_names(self, names: Iterable[str]) -> List[TagEntity]:  # noqa: UP006
        existing_stmt = select(TagEntity).where(TagEntity.name.in_(list(names)))
        existing = (await self._session.execute(existing_stmt)).scalars().all()
        existing_map = {e.name: e for e in existing}
        created: list[TagEntity] = []
        for name in names:
            if name in existing_map:
                continue
            tag = TagEntity(id=str(uuid.uuid4()), name=name)
            self._session.add(tag)
            created.append(tag)
        if created:
            await self._session.flush()
        return list(existing_map.values()) + created


__all__ = ("TagRepository",)
