from __future__ import annotations

from .models import Pet, PetCreate, PetUpdate
from .pet_repository import DBPetRepository
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
        repo: DBPetRepository,
        tag_repo: TagRepository,
        category_repo: CategoryRepository,
        user_repo: UserRepository,
    ) -> None:
        self._repo = repo
        self._tag_repo = tag_repo
        self._category_repo = category_repo
        self._user_repo = user_repo

    async def create(self, payload: PetCreate) -> Pet:
        """Create a new pet with validation and tag management.

        This operation involves multiple repository calls and should be transactional
        to ensure consistency between tag creation/validation and pet creation.
        """
        async with transactional(self._repo.session):
            tag_ids: list[str] | None = None
            if payload.tags:
                # Ensure tags exist and preserve order by mapping names -> ids
                tag_rows = await self._tag_repo.ensure_exist_by_names(payload.tags)
                by_name = {t.name: t.id for t in tag_rows}
                tag_ids = [by_name[name] for name in payload.tags]

            # Create pet entity
            pet_db = await self._repo.create(payload, tag_ids=tag_ids)

            # Get with selective relations - only load what we need for the response
            # For creation, we typically need all relations for the response
            pet_db_with_relations = await self._repo.get_with_options(pet_db.id, PetQueryOptions.all())
            return PetMapper.to_domain(pet_db_with_relations)

    async def list(self, *, page: int = 1, size: int = 10, include_relations: bool = True) -> tuple[list[Pet], int]:
        """List pets with pagination and selective relation loading.

        Args:
            page: Page number (1-based)
            size: Page size
            include_relations: If True, includes all relations. If False, minimal loading.
        """
        async with transactional(self._repo.session):
            # Choose query options based on requirement
            query_options = PetQueryOptions.all() if include_relations else PetQueryOptions.minimal()

            # Get DB entities with selective relations
            pet_dbs, total = await self._repo.list_with_options(page=page, size=size, options=query_options)

            # Convert to domain models using mapper
            items = [PetMapper.to_domain(pet_db) for pet_db in pet_dbs]
            return items, total

    async def get(self, entity_id: PetId, *, include_relations: bool = True) -> Pet:
        """Get a pet by ID with selective relation loading.

        Args:
            entity_id: Pet ID
            include_relations: If True, includes all relations. If False, minimal loading.
        """
        async with transactional(self._repo.session):
            # Choose query options based on requirement
            query_options = PetQueryOptions.all() if include_relations else PetQueryOptions.minimal()

            # Get DB entity with selective relations
            pet_db = await self._repo.get_with_options(entity_id, query_options)

            # Convert to domain model using mapper
            return PetMapper.to_domain(pet_db)

    async def patch(self, entity_id: PetId, payload: PetUpdate) -> Pet:
        """Update a pet partially with transactional tag management and proper domain conversion."""
        async with transactional(self._repo.session):
            tag_ids: list[str] | None = None
            if payload.tags is not MISSING:  # type: ignore[comparison-overlap]
                # deduplicate while preserving order
                deduped = list(dict.fromkeys(payload.tags))
                tag_rows = await self._tag_repo.ensure_exist_by_names(deduped)
                by_name = {t.name: t.id for t in tag_rows}
                tag_ids = [by_name[name] for name in deduped]

            # Patch and get updated DB entity
            pet_db = await self._repo.patch(entity_id, payload, tag_ids=tag_ids)

            # Get with all relations for the response (update operation typically needs full data)
            pet_db_with_relations = await self._repo.get_with_options(pet_db.id, PetQueryOptions.all())
            return PetMapper.to_domain(pet_db_with_relations)

    async def delete(self, entity_id: PetId) -> None:
        """Delete a pet by ID with transaction management."""
        async with transactional(self._repo.session):
            await self._repo.delete(entity_id)


__all__ = ("PetService",)
