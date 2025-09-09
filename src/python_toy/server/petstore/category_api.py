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
    _service: CategoryService = Depends(_service_dep)

    @router.post("/v1/categories", status_code=HTTP_201_CREATED)
    async def create(self, payload: CategoryCreate) -> Category:
        return await self._service.create(payload)

    @router.get("/v1/categories")
    async def list(
        self,
        page: Annotated[int, Query(ge=1)] = 1,
        size: Annotated[int, Query(ge=1, le=100)] = 10,
    ) -> PageResponse[Category]:
        return await self._service.list(page, size)

    @router.get("/v1/categories/{entity_id}")
    async def get(self, entity_id: CategoryId) -> Category:
        return await self._service.get(entity_id)

    @router.delete("/v1/categories/{entity_id}")
    async def delete(self, entity_id: CategoryId) -> EmptyResponse:
        await self._service.delete(entity_id)
        return EmptyResponse()


__all__ = ("router",)
