from __future__ import annotations

from .models import Pet, PetCreate, PetUpdate, PetId
from .repository import InMemoryPetRepository


class PetService:
    """Application service for Pet domain.

    Currently a thin layer delegating to the repository, prepared for future
    business logic, validation, and cross-cutting concerns.
    """

    def __init__(self, repo: InMemoryPetRepository) -> None:
        self._repo = repo

    async def create(self, payload: PetCreate) -> Pet:
        return await self._repo.create(payload)

    async def list(self) -> list[Pet]:
        return await self._repo.list()

    async def get(self, pet_id: PetId) -> Pet:
        return await self._repo.get(pet_id)

    async def patch(self, pet_id: PetId, payload: PetUpdate) -> Pet:
        return await self._repo.patch(pet_id, payload)

    async def delete(self, pet_id: PetId) -> None:
        await self._repo.delete(pet_id)


__all__ = ("PetService",)
