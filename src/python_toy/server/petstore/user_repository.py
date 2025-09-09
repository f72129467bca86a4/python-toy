from __future__ import annotations

from sqlalchemy import delete, func, select

from python_toy.server.infra.error import EntityNotFoundException
from python_toy.server.petstore.db_models import UserEntity
from .base_repository import BaseRepository, SessionSupplier


class UserRepository(BaseRepository[UserEntity]):
    def __init__(self, session_supplier: SessionSupplier) -> None:
        super().__init__(UserEntity, session_supplier)

    async def list(self, *, page: int = 1, size: int = 10) -> tuple[list[UserEntity], int]:
        total = int((await self._session.execute(select(func.count()).select_from(UserEntity))).scalar_one())

        q = select(UserEntity).order_by(UserEntity.username).offset((page - 1) * size).limit(size)
        items = (await self._session.execute(q)).scalars().all()
        return list(items), total

    async def get(self, entity_id: str) -> UserEntity:
        return await self.get_required(entity_id)

    async def delete(self, entity_id: str) -> None:
        res = await self._session.execute(delete(UserEntity).where(UserEntity.id == entity_id))
        if res.rowcount == 0:
            raise EntityNotFoundException(entity_type=self.entity_type, entity_id=entity_id)


__all__ = ("UserRepository",)
