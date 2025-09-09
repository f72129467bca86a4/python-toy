from __future__ import annotations

from python_toy.server.model.common import PageResponse
from python_toy.server.infra.transaction import transactional
from .models import Tag, TagCreate
from .tag_repository import TagRepository
from .mappers import TagMapper


class TagService:
    """Application service for Tag domain."""

    def __init__(self, repo: TagRepository) -> None:
        self._repo = repo

    async def create(self, payload: TagCreate) -> Tag:
        async with transactional(self._repo._session):
            entity = TagMapper.to_entity(payload)
            entity = await self._repo.create(entity)
            return TagMapper.to_domain(entity)

    async def list(self, page: int, size: int) -> PageResponse[Tag]:
        async with transactional(self._repo._session):
            entities, total = await self._repo.list(page=page, size=size)
            items = [TagMapper.to_domain(item) for item in entities]
            return PageResponse.create(items, total, page, size)

    async def get(self, entity_id: str) -> Tag:
        async with transactional(self._repo._session):
            entity = await self._repo.get_required(entity_id)
            return TagMapper.to_domain(entity)

    async def delete(self, entity_id: str) -> None:
        async with transactional(self._repo._session):
            await self._repo.delete(entity_id)


__all__ = ("TagService",)
