from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from starlette.status import HTTP_201_CREATED
from python_toy.server.model.common import ListResponse, EmptyResponse
from .models import Pet, PetCreate, PetUpdate, PetId
from python_toy.server.infra.container import Container
from fastapi_utils.cbv import cbv
from .service import PetService


def _pet_service_dep(request: Request) -> PetService:
    container: Container = request.app.state.container
    return container.pet_service()


router = APIRouter(tags=["pets"])


@cbv(router)
class PetRoutes:
    service: PetService = Depends(_pet_service_dep)

    @router.post("/v1/pets", status_code=HTTP_201_CREATED)
    async def create_pet(self, payload: PetCreate) -> Pet:
        return await self.service.create(payload)

    @router.get("/v1/pets")
    async def list_pets(self) -> ListResponse[Pet]:
        return ListResponse.of(await self.service.list())

    @router.get("/v1/pets/{pet_id}")
    async def get_pet(self, pet_id: PetId) -> Pet:
        return await self.service.get(pet_id)

    @router.patch("/v1/pets/{pet_id}")
    async def patch_pet(self, pet_id: PetId, payload: PetUpdate) -> Pet:
        return await self.service.patch(pet_id, payload)

    @router.delete("/v1/pets/{pet_id}")
    async def delete_pet(self, pet_id: PetId) -> EmptyResponse:
        await self.service.delete(pet_id)
        return EmptyResponse()
