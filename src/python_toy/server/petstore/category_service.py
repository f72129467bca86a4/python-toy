from __future__ import annotations

from python_toy.server.model.common import PageResponse
from python_toy.server.infra.database import transactional
from .models import Category, CategoryCreate
from .category_repository import CategoryRepository
from .mappers import CategoryMapper


class CategoryService:
    def __init__(self, repo: CategoryRepository) -> None:
        self._repo = repo

    async def create(self, payload: CategoryCreate) -> Category:
        async with transactional(self._repo.session):
            category_db = await self._repo.create(payload)
            return CategoryMapper.to_domain(category_db)

    async def list(self, page: int, size: int) -> PageResponse[Category]:
        async with transactional(self._repo.session):
            items_db, total = await self._repo.list(page=page, size=size)
            items = [CategoryMapper.to_domain(item) for item in items_db]
            return PageResponse.create(items, total, page, size)

    async def get(self, entity_id: str) -> Category:
        async with transactional(self._repo.session):
            category_db = await self._repo.get_required(entity_id)
            return CategoryMapper.to_domain(category_db)

    async def delete(self, entity_id: str) -> None:
        async with transactional(self._repo.session):
            await self._repo.delete(entity_id)


__all__ = ("CategoryService",)
