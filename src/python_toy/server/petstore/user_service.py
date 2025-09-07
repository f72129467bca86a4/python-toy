from __future__ import annotations

from python_toy.server.model.common import PageResponse
from python_toy.server.infra.database import transactional
from .models import User, UserCreate
from .user_repository import UserRepository
from .mappers import UserMapper


class UserService:
    def __init__(self, repo: UserRepository) -> None:
        self._repo = repo

    async def create(self, payload: UserCreate) -> User:
        async with transactional(self._repo.session):
            user_db = await self._repo.create(payload)
            return UserMapper.to_domain(user_db)

    async def list(self, page: int, size: int) -> PageResponse[User]:
        async with transactional(self._repo.session):
            items_db, total = await self._repo.list(page=page, size=size)
            items = [UserMapper.to_domain(item) for item in items_db]
            return PageResponse.create(items, total, page, size)

    async def get(self, entity_id: str) -> User:
        async with transactional(self._repo.session):
            user_db = await self._repo.get_required(entity_id)
            return UserMapper.to_domain(user_db)

    async def delete(self, entity_id: str) -> None:
        async with transactional(self._repo.session):
            await self._repo.delete(entity_id)


__all__ = ("UserService",)
