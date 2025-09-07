from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Request, Query
from starlette.status import HTTP_201_CREATED
from python_toy.server.model.common import PageResponse, EmptyResponse
from .models import Pet, PetCreate, PetUpdate
from python_toy.server.infra.container import Container
from fastapi_utils.cbv import cbv
from .pet_service import PetService
from sqlalchemy.ext.asyncio import AsyncSession
from python_toy.server.infra.database import get_db
from python_toy.server.petstore.id_type import PetId


def _pet_service_dep(request: Request, session: Annotated[AsyncSession, Depends(get_db)]) -> PetService:
    container: Container = request.app.state.container
    # Construct dependencies sharing the same DB session
    repo = container.pet_repository(session=session)
    tag_repo = container.tag_repository(session=session)
    category_repo = container.category_repository(session=session)
    user_repo = container.user_repository(session=session)
    return container.pet_service(repo=repo, tag_repo=tag_repo, category_repo=category_repo, user_repo=user_repo)


router = APIRouter(tags=["pets"])


@cbv(router)
class PetRoutes:
    service: PetService = Depends(_pet_service_dep)

    @router.post("/v1/pets", status_code=HTTP_201_CREATED)
    async def create_pet(self, payload: PetCreate) -> Pet:
        """Create a new pet."""
        return await self.service.create(payload)

    @router.get("/v1/pets")
    async def list_pets(
        self,
        page: Annotated[int, Query(ge=1)] = 1,
        size: Annotated[int, Query(ge=1, le=100)] = 10,
    ) -> PageResponse[Pet]:
        """List pets with pagination."""
        items, total = await self.service.list(page=page, size=size)
        return PageResponse.create(items, total, page, size)

    @router.get("/v1/pets/{pet_id}")
    async def get_pet(self, pet_id: PetId) -> Pet:
        """Get a pet by ID."""
        return await self.service.get(pet_id)

    @router.patch("/v1/pets/{pet_id}")
    async def patch_pet(self, pet_id: PetId, payload: PetUpdate) -> Pet:
        """Update a pet partially."""
        return await self.service.patch(pet_id, payload)

    @router.delete("/v1/pets/{pet_id}")
    async def delete_pet(self, pet_id: PetId) -> EmptyResponse:
        """Delete a pet by ID."""
        await self.service.delete(pet_id)
        return EmptyResponse()


__all__ = ("router",)
