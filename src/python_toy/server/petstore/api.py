from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
import itertools
from typing import Annotated

from fastapi import APIRouter
from pydantic import BaseModel, Field
from pydantic.experimental.missing_sentinel import MISSING
from python_toy.server.infra.error import EntityNotFoundException
from python_toy.server.model.common import ListResponse, EmptyResponse
from starlette.status import HTTP_201_CREATED

router = APIRouter(tags=["pets"])

type PetId = Annotated[str, Field(min_length=1, max_length=64, pattern=r"^[a-zA-Z0-9]+$")]


class Pet(BaseModel):
    id: PetId
    name: str = Field(min_length=1, max_length=100)
    tags: list[str] = Field(default_factory=list)


class PetCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100, examples=["야옹이"])
    tags: list[str] = Field(default_factory=list, examples=[["cat", "cute"]])


class PetUpdate(BaseModel):
    name: str | MISSING = Field(default=MISSING, min_length=1, max_length=100)  # type: ignore[valid-type]
    tags: list[str] | MISSING = MISSING  # type: ignore[valid-type]


@dataclass
class InMemoryPetRepository:
    _lock: asyncio.Lock = field(default_factory=asyncio.Lock)
    _data: dict[PetId, Pet] = field(default_factory=dict)
    _seq: itertools.count[int] = field(default_factory=lambda: itertools.count(1))

    async def create(self, payload: PetCreate) -> Pet:
        async with self._lock:
            new_id = str(next(self._seq))
            pet = Pet(id=new_id, name=payload.name, tags=list(payload.tags))
            self._data[new_id] = pet
            return pet

    async def list(self) -> list[Pet]:
        async with self._lock:
            return list(self._data.values())

    def _get(self, pet_id: PetId) -> Pet:
        pet = self._data.get(pet_id)
        if not pet:
            raise EntityNotFoundException(entity_id=pet_id)
        return pet

    async def get(self, pet_id: PetId) -> Pet:
        async with self._lock:
            return self._get(pet_id)

    async def patch(self, pet_id: PetId, payload: PetUpdate) -> Pet:
        async with self._lock:
            pet = self._get(pet_id)
            updated = pet.model_copy(
                update={
                    "name": payload.name if payload.name is not MISSING else pet.name,  # type: ignore[comparison-overlap]
                    "tags": payload.tags if payload.tags is not MISSING else pet.tags,  # type: ignore[comparison-overlap]
                }
            )
            self._data[pet_id] = updated
            return updated

    async def delete(self, pet_id: PetId) -> None:
        async with self._lock:
            if pet_id not in self._data:
                raise EntityNotFoundException(entity_id=pet_id)
            del self._data[pet_id]


_repository = InMemoryPetRepository()


@router.post("/v1/pets", status_code=HTTP_201_CREATED)
async def create_pet(payload: PetCreate) -> Pet:
    return await _repository.create(payload)


@router.get("/v1/pets")
async def list_pets() -> ListResponse[Pet]:
    return ListResponse.of(await _repository.list())


@router.get("/v1/pets/{pet_id}")
async def get_pet(pet_id: PetId) -> Pet:
    return await _repository.get(pet_id)


@router.patch("/v1/pets/{pet_id}")
async def patch_pet(pet_id: PetId, payload: PetUpdate) -> Pet:
    return await _repository.patch(pet_id, payload)


@router.delete("/v1/pets/{pet_id}")
async def delete_pet(pet_id: PetId) -> EmptyResponse:
    await _repository.delete(pet_id)
    return EmptyResponse()
