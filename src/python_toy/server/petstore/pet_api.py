from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Request, Query
from starlette.status import HTTP_201_CREATED
from python_toy.server.model.common import PageResponse, EmptyResponse
from .models import Pet, PetCreate, PetUpdate
from fastapi_utils.cbv import cbv
from .pet_service import PetService
from python_toy.server.petstore.id_type import PetId


def _pet_service_dep(request: Request) -> PetService:
    from python_toy.server.infra.container import Container

    container: Container = request.app.state.container
    return container.pet_service()


router = APIRouter(tags=["pets"])


@cbv(router)
class PetRoutes:
    _service: PetService = Depends(_pet_service_dep)

    @router.post("/v1/pets", status_code=HTTP_201_CREATED)
    async def create_pet(self, payload: PetCreate) -> Pet:
        return await self._service.create(payload)

    @router.get("/v1/pets")
    async def list_pets(
        self,
        page: Annotated[int, Query(ge=1)] = 1,
        size: Annotated[int, Query(ge=1, le=100)] = 10,
    ) -> PageResponse[Pet]:
        items, total = await self._service.list(page=page, size=size)
        return PageResponse.create(items, total, page, size)

    @router.get("/v1/pets/{pet_id}")
    async def get_pet(self, pet_id: PetId) -> Pet:
        return await self._service.get(pet_id)

    @router.patch("/v1/pets/{pet_id}")
    async def patch_pet(self, pet_id: PetId, payload: PetUpdate) -> Pet:
        return await self._service.patch(pet_id, payload)

    @router.delete("/v1/pets/{pet_id}")
    async def delete_pet(self, pet_id: PetId) -> EmptyResponse:
        await self._service.delete(pet_id)
        return EmptyResponse()


__all__ = ("router",)
