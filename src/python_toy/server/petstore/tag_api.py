from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query, Request
from fastapi_utils.cbv import cbv
from starlette.status import HTTP_201_CREATED

from python_toy.server.model.common import EmptyResponse, PageResponse
from .tag_service import TagService
from .models import Tag, TagCreate
from python_toy.server.petstore.id_type import TagId


router = APIRouter(tags=["tags"])


def _service_dep(request: Request) -> TagService:
    from python_toy.server.infra.container import Container

    container: Container = request.app.state.container
    return container.tag_service()


@cbv(router)
class TagRoutes:
    _service: TagService = Depends(_service_dep)

    @router.post("/v1/tags", status_code=HTTP_201_CREATED)
    async def create(self, payload: TagCreate) -> Tag:
        return await self._service.create(payload)

    @router.get("/v1/tags")
    async def list(
        self,
        page: Annotated[int, Query(ge=1)] = 1,
        size: Annotated[int, Query(ge=1, le=100)] = 10,
    ) -> PageResponse[Tag]:
        return await self._service.list(page, size)

    @router.get("/v1/tags/{entity_id}")
    async def get(self, entity_id: TagId) -> Tag:
        return await self._service.get(entity_id)

    @router.delete("/v1/tags/{entity_id}")
    async def delete(self, entity_id: TagId) -> EmptyResponse:
        await self._service.delete(entity_id)
        return EmptyResponse()


__all__ = ("router",)
