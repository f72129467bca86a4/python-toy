from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query, Request
from fastapi_utils.cbv import cbv
from starlette.status import HTTP_201_CREATED

from python_toy.server.model.common import EmptyResponse, PageResponse
from .category_service import CategoryService
from .models import Category, CategoryCreate
from python_toy.server.petstore.id_type import CategoryId


def _service_dep(request: Request) -> CategoryService:
    from python_toy.server.infra.container import Container

    container: Container = request.app.state.container
    return container.category_service()


router = APIRouter(tags=["categories"])


@cbv(router)
class CategoryRoutes:
    svc: CategoryService = Depends(_service_dep)

    @router.post("/v1/categories", status_code=HTTP_201_CREATED)
    async def create(self, payload: CategoryCreate) -> Category:
        """Create a new category."""
        return await self.svc.create(payload)

    @router.get("/v1/categories")
    async def list(
        self,
        page: Annotated[int, Query(ge=1)] = 1,
        size: Annotated[int, Query(ge=1, le=100)] = 10,
    ) -> PageResponse[Category]:
        """List categories with pagination."""
        return await self.svc.list(page, size)

    @router.get("/v1/categories/{entity_id}")
    async def get(self, entity_id: CategoryId) -> Category:
        """Get a category by ID."""
        return await self.svc.get(entity_id)

    @router.delete("/v1/categories/{entity_id}")
    async def delete(self, entity_id: CategoryId) -> EmptyResponse:
        """Delete a category by ID."""
        await self.svc.delete(entity_id)
        return EmptyResponse()


__all__ = ("router",)
