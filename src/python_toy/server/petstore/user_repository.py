from __future__ import annotations

import uuid

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from python_toy.server.infra.error import EntityNotFoundException, DuplicateEntityException
from python_toy.server.petstore.db_models import UserEntity
from .models import UserCreate
from .base_repository import BaseRepository


class UserRepository(BaseRepository[UserEntity, UserCreate, UserEntity]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, UserEntity)

    def _create_db_entity(self, payload: UserCreate) -> UserEntity:
        return UserEntity(
            id=str(uuid.uuid4()),
            username=payload.username,
            first_name=payload.first_name,
            last_name=payload.last_name,
            email=payload.email,
            password=payload.password,
            phone=payload.phone,
        )

    async def create(self, payload: UserCreate) -> UserEntity:
        """Create a new user."""
        try:
            return await self.create_db_entity(payload)
        except DuplicateEntityException:
            raise

    async def list(self, *, page: int = 1, size: int = 10) -> tuple[list[UserEntity], int]:
        """List User entities ordered by username."""
        total = int((await self.session.execute(select(func.count()).select_from(UserEntity))).scalar_one())

        q = select(UserEntity).order_by(UserEntity.username).offset((page - 1) * size).limit(size)
        items = (await self.session.execute(q)).scalars().all()
        return list(items), total

    async def get(self, entity_id: str) -> UserEntity:
        return await self.get_required(entity_id)

    async def delete(self, entity_id: str) -> None:
        """Delete a user by ID."""
        res = await self.session.execute(delete(UserEntity).where(UserEntity.id == entity_id))
        if res.rowcount == 0:
            raise EntityNotFoundException(entity_type="User", entity_id=entity_id)


__all__ = ("UserRepository",)
