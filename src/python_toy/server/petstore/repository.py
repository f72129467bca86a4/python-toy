from __future__ import annotations

import asyncio
import itertools
from dataclasses import dataclass, field

from python_toy.server.infra.error import EntityNotFoundException
from .models import PetId, Pet, PetCreate, PetUpdate
from pydantic.experimental.missing_sentinel import MISSING


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


__all__ = ("InMemoryPetRepository",)
