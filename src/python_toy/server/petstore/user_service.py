from __future__ import annotations

from python_toy.server.model.common import PageResponse
from python_toy.server.infra.transaction import transactional
from .models import User, UserCreate
from .user_repository import UserRepository
from .mappers import UserMapper


class UserService:
    def __init__(self, repo: UserRepository) -> None:
        self._repo = repo

    async def create(self, payload: UserCreate) -> User:
        async with transactional(self._repo._session):
            entity = UserMapper.to_entity(payload)
            entity = await self._repo.create(entity)
            return UserMapper.to_domain(entity)

    async def list(self, page: int, size: int) -> PageResponse[User]:
        async with transactional(self._repo._session):
            entities, total = await self._repo.list(page=page, size=size)
            items = [UserMapper.to_domain(item) for item in entities]
            return PageResponse.create(items, total, page, size)

    async def get(self, entity_id: str) -> User:
        async with transactional(self._repo._session):
            entity = await self._repo.get_required(entity_id)
            return UserMapper.to_domain(entity)

    async def delete(self, entity_id: str) -> None:
        async with transactional(self._repo._session):
            await self._repo.delete(entity_id)


__all__ = ("UserService",)
