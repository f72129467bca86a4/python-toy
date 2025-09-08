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
        """Create a new tag."""
        async with transactional(self._repo.session):
            tag_db = await self._repo.create(payload)
            return TagMapper.to_domain(tag_db)

    async def list(self, page: int, size: int) -> PageResponse[Tag]:
        """List tags with pagination."""
        async with transactional(self._repo.session):
            items_db, total = await self._repo.list(page=page, size=size)
            items = [TagMapper.to_domain(item) for item in items_db]
            return PageResponse.create(items, total, page, size)

    async def get(self, entity_id: str) -> Tag:
        """Get a tag by ID."""
        async with transactional(self._repo.session):
            tag_db = await self._repo.get_required(entity_id)
            return TagMapper.to_domain(tag_db)

    async def delete(self, entity_id: str) -> None:
        """Delete a tag by ID."""
        async with transactional(self._repo.session):
            await self._repo.delete(entity_id)


__all__ = ("TagService",)
