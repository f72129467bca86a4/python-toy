from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query, Request
from fastapi_utils.cbv import cbv
from starlette.status import HTTP_201_CREATED
from sqlalchemy.ext.asyncio import AsyncSession

from python_toy.server.infra.database import get_db
from python_toy.server.infra.container import Container
from python_toy.server.model.common import EmptyResponse, PageResponse
from .tag_service import TagService
from .models import Tag, TagCreate
from python_toy.server.petstore.id_type import TagId


router = APIRouter(tags=["tags"])


def _service_dep(request: Request, session: Annotated[AsyncSession, Depends(get_db)]) -> TagService:
    container: Container = request.app.state.container
    repo = container.tag_repository(session=session)
    return container.tag_service(repo=repo)


@cbv(router)
class TagRoutes:
    svc: TagService = Depends(_service_dep)

    @router.post("/v1/tags", status_code=HTTP_201_CREATED)
    async def create(self, payload: TagCreate) -> Tag:
        """Create a new tag."""
        return await self.svc.create(payload)

    @router.get("/v1/tags")
    async def list(
        self,
        page: Annotated[int, Query(ge=1)] = 1,
        size: Annotated[int, Query(ge=1, le=100)] = 10,
    ) -> PageResponse[Tag]:
        """List tags with pagination."""
        return await self.svc.list(page, size)

    @router.get("/v1/tags/{entity_id}")
    async def get(self, entity_id: TagId) -> Tag:
        """Get a tag by ID."""
        return await self.svc.get(entity_id)

    @router.delete("/v1/tags/{entity_id}")
    async def delete(self, entity_id: TagId) -> EmptyResponse:
        """Delete a tag by ID."""
        await self.svc.delete(entity_id)
        return EmptyResponse()


__all__ = ("router",)
