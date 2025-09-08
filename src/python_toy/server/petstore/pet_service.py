from __future__ import annotations

from .models import Pet, PetCreate, PetUpdate
from .pet_repository import PetRepository
from .tag_repository import TagRepository
from .category_repository import CategoryRepository
from .user_repository import UserRepository
from .query_options import PetQueryOptions
from pydantic.experimental.missing_sentinel import MISSING
from python_toy.server.petstore.id_type import PetId
from python_toy.server.infra.transaction import transactional

# Import mappers for domain conversion
from python_toy.server.petstore.mappers import PetMapper


class PetService:
    """Application service for Pet domain.

    Handles business logic, validation, and cross-cutting concerns for pets.
    Orchestrates multiple repositories and provides clean domain conversion.
    """

    def __init__(
        self,
        repo: PetRepository,
        tag_repo: TagRepository,
        category_repo: CategoryRepository,
        user_repo: UserRepository,
    ) -> None:
        self._repo = repo
        self._tag_repo = tag_repo
        self._category_repo = category_repo
        self._user_repo = user_repo

    async def create(self, payload: PetCreate) -> Pet:
        async with transactional(self._repo._session):
            tag_ids: list[str] | None = None
            if payload.tags:
                # Ensure tags exist and preserve order by mapping names -> ids
                tag_rows = await self._tag_repo.ensure_exist_by_names(payload.tags)
                by_name = {t.name: t.id for t in tag_rows}
                tag_ids = [by_name[name] for name in payload.tags]

            pet_entity = PetMapper.to_entity(payload)
            pet_entity = await self._repo.create(pet_entity, tag_ids=tag_ids)

            # Get with selective relations - only load what we need for the response
            # For creation, we typically need all relations for the response
            pet_db_with_relations = await self._repo.get_with_options(pet_entity.id, PetQueryOptions.all())
            return PetMapper.to_domain(pet_db_with_relations)

    async def list(self, *, page: int = 1, size: int = 10, include_relations: bool = True) -> tuple[list[Pet], int]:
        """List pets with pagination and selective relation loading.

        :param page: Page number (1-based)
        :param size: Page size
        :param include_relations: If True, includes all relations. If False, minimal loading.
        """
        async with transactional(self._repo._session):
            query_options = PetQueryOptions.all() if include_relations else PetQueryOptions.minimal()

            entities, total = await self._repo.list_with_options(page=page, size=size, options=query_options)

            items = [PetMapper.to_domain(it) for it in entities]
            return items, total

    async def get(self, entity_id: PetId, *, include_relations: bool = True) -> Pet:
        async with transactional(self._repo._session):
            query_options = PetQueryOptions.all() if include_relations else PetQueryOptions.minimal()

            entity = await self._repo.get_with_options(entity_id, query_options)

            return PetMapper.to_domain(entity)

    async def patch(self, entity_id: PetId, payload: PetUpdate) -> Pet:
        async with transactional(self._repo._session):
            tag_ids: list[str] | None = None
            if payload.tags is not MISSING:  # type: ignore[comparison-overlap]
                # deduplicate while preserving order
                deduped = list(dict.fromkeys(payload.tags))
                tag_rows = await self._tag_repo.ensure_exist_by_names(deduped)
                by_name = {t.name: t.id for t in tag_rows}
                tag_ids = [by_name[name] for name in deduped]

            entity = await self._repo.patch(entity_id, payload, tag_ids=tag_ids)

            entity_with_relations = await self._repo.get_with_options(entity.id, PetQueryOptions.all())
            return PetMapper.to_domain(entity_with_relations)

    async def delete(self, entity_id: PetId) -> None:
        async with transactional(self._repo._session):
            await self._repo.delete(entity_id)


__all__ = ("PetService",)
