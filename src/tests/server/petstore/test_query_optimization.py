"""Tests for query optimization and performance features."""

from sqlalchemy.ext.asyncio import AsyncSession

from python_toy.server.petstore.models import PetCreate
from python_toy.server.petstore.pet_repository import DBPetRepository
from python_toy.server.petstore.pet_service import PetService
from python_toy.server.petstore.query_options import PetQueryOptions
from python_toy.server.petstore.tag_repository import TagRepository
from python_toy.server.petstore.category_repository import CategoryRepository
from python_toy.server.petstore.user_repository import UserRepository


class TestQueryOptions:
    """Test query optimization features through PetQueryOptions."""

    async def test_query_options_factory_methods(self) -> None:
        """Test query options factory methods provide correct configurations."""
        # Test all relations enabled
        all_options = PetQueryOptions.all()
        assert all_options.include_category is True
        assert all_options.include_owner is True
        assert all_options.include_tags is True

        # Test minimal (no relations)
        minimal_options = PetQueryOptions.minimal()
        assert minimal_options.include_category is False
        assert minimal_options.include_owner is False
        assert minimal_options.include_tags is False

        # Test selective loading
        category_options = PetQueryOptions.with_category()
        assert category_options.include_category is True
        assert category_options.include_owner is False
        assert category_options.include_tags is False

        owner_options = PetQueryOptions.with_owner()
        assert owner_options.include_category is False
        assert owner_options.include_owner is True
        assert owner_options.include_tags is False

        tags_options = PetQueryOptions.with_tags()
        assert tags_options.include_category is False
        assert tags_options.include_owner is False
        assert tags_options.include_tags is True

    async def test_pet_repository_query_options(self, db_session: AsyncSession) -> None:
        """Test repository query options integration."""
        repo = DBPetRepository(db_session)

        # Create a test pet
        payload = PetCreate(name="Query Test Pet", status="available")
        pet_db = await repo.create(payload)

        # Test minimal loading (no relations eagerly loaded)
        minimal_options = PetQueryOptions.minimal()
        pet_minimal = await repo.get_with_options(pet_db.id, minimal_options)
        assert pet_minimal.name == "Query Test Pet"
        assert pet_minimal.id == pet_db.id

        # Test selective loading - category only
        category_options = PetQueryOptions.with_category()
        pet_with_category = await repo.get_with_options(pet_db.id, category_options)
        assert pet_with_category.name == "Query Test Pet"

        # Verify options configuration
        assert category_options.include_category is True
        assert category_options.include_owner is False
        assert category_options.include_tags is False

    async def test_pet_service_optimized_operations(self, db_session: AsyncSession) -> None:
        """Test service layer optimization features."""
        # Setup all repositories
        pet_repo = DBPetRepository(db_session)
        tag_repo = TagRepository(db_session)
        category_repo = CategoryRepository(db_session)
        user_repo = UserRepository(db_session)

        service = PetService(pet_repo, tag_repo, category_repo, user_repo)

        # Create test pet
        payload = PetCreate(name="Service Test Pet", status="available", tags=["optimization"])
        created_pet = await service.create(payload)
        assert created_pet.name == "Service Test Pet"
        assert created_pet.tags == ["optimization"]

        # Test listing with relation control
        pets_minimal, total_minimal = await service.list(page=1, size=10, include_relations=False)
        assert len(pets_minimal) == 1
        assert total_minimal == 1

        pets_full, total_full = await service.list(page=1, size=10, include_relations=True)
        assert len(pets_full) == 1
        assert total_full == 1

        # Both should return same count, but different relation loading
        assert total_minimal == total_full
