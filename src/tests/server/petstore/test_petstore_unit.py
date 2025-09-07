"""Unit tests for Petstore repositories and services."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from python_toy.server.infra.error import EntityNotFoundException
from python_toy.server.infra.error.exceptions import DuplicateEntityException, ForeignKeyViolationException
from python_toy.server.petstore.models import (
    PetCreate,
    CategoryCreate,
    TagCreate,
    UserCreate,
)
from python_toy.server.petstore.pet_repository import DBPetRepository
from python_toy.server.petstore.pet_service import PetService
from python_toy.server.petstore.category_repository import CategoryRepository
from python_toy.server.petstore.tag_repository import TagRepository
from python_toy.server.petstore.user_repository import UserRepository


class TestCategoryRepository:
    """Test CategoryRepository unit operations."""

    async def test_create_and_get_category(self, db_session: AsyncSession) -> None:
        """Test creating and retrieving a category."""
        repo = CategoryRepository(db_session)
        payload = CategoryCreate(name="Test Category")

        # Create
        category = await repo.create(payload)
        assert category.name == "Test Category"
        assert category.id is not None
        category_id = category.id

        # Get by ID
        retrieved = await repo.get(category_id)
        assert retrieved is not None
        assert retrieved.name == "Test Category"
        assert retrieved.id == category_id

    async def test_list_categories_with_pagination(self, db_session: AsyncSession) -> None:
        """Test listing categories with pagination."""
        repo = CategoryRepository(db_session)

        # Create test data
        created_categories = []
        for i in range(3):
            category = await repo.create(CategoryCreate(name=f"Category {i}"))
            created_categories.append(category)

        # Test pagination
        categories, total = await repo.list(page=1, size=2)
        assert total == 3
        assert len(categories) == 2

        # Test second page
        categories_page2, total_page2 = await repo.list(page=2, size=2)
        assert total_page2 == 3
        assert len(categories_page2) == 1

    async def test_delete_category(self, db_session: AsyncSession) -> None:
        """Test deleting a category."""
        repo = CategoryRepository(db_session)
        category = await repo.create(CategoryCreate(name="To Delete"))

        # Delete
        await repo.delete(category.id)

        # Verify deletion - should raise EntityNotFoundException
        with pytest.raises(EntityNotFoundException):
            await repo.get(category.id)


class TestTagRepository:
    """Test TagRepository unit operations."""

    async def test_create_and_get_tag(self, db_session: AsyncSession) -> None:
        """Test creating and retrieving a tag."""
        repo = TagRepository(db_session)
        payload = TagCreate(name="Test Tag")

        # Create
        tag = await repo.create(payload)
        assert tag.name == "Test Tag"
        assert tag.id is not None

        # Get by ID
        retrieved = await repo.get(tag.id)
        assert retrieved is not None
        assert retrieved.name == "Test Tag"

    async def test_ensure_exist_by_names(self, db_session: AsyncSession) -> None:
        """Test ensuring tags exist by names (create if not exists)."""
        repo = TagRepository(db_session)

        # First call - should create new tags
        tags = await repo.ensure_exist_by_names(["new_tag1", "new_tag2"])
        assert len(tags) == 2
        tag_names = [tag.name for tag in tags]
        assert "new_tag1" in tag_names
        assert "new_tag2" in tag_names

        # Second call - should return existing tags
        tags_again = await repo.ensure_exist_by_names(["new_tag1", "new_tag2"])
        assert len(tags_again) == 2

        # Should be same IDs
        original_ids = {tag.id for tag in tags}
        repeat_ids = {tag.id for tag in tags_again}
        assert original_ids == repeat_ids


class TestUserRepository:
    """Test UserRepository unit operations."""

    async def test_create_and_get_user(self, db_session: AsyncSession) -> None:
        """Test creating and retrieving a user."""
        repo = UserRepository(db_session)
        payload = UserCreate(
            username="testuser", first_name="Test", last_name="User", email="test@example.com", password="password123"
        )

        # Create
        user = await repo.create(payload)
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.id is not None

        # Get by ID
        retrieved = await repo.get(user.id)
        assert retrieved is not None
        assert retrieved.username == "testuser"


class TestPetRepository:
    """Test PetRepository unit operations."""

    async def test_create_simple_pet(self, db_session: AsyncSession) -> None:
        """Test creating a simple pet without relationships."""
        repo = DBPetRepository(db_session)
        payload = PetCreate(
            name="Simple Pet", status="available", photo_urls=["http://example.com/photo.jpg"], tags=["simple"]
        )

        pet = await repo.create(payload)
        assert pet.name == "Simple Pet"
        assert pet.status == "available"
        assert pet.id is not None
        # Note: tags are handled separately in repository layer and require service layer for proper mapping

    async def test_create_pet_with_relationships(self, db_session: AsyncSession) -> None:
        """Test creating a pet with category and owner relationships."""
        # Setup dependencies
        category_repo = CategoryRepository(db_session)
        user_repo = UserRepository(db_session)

        category_repo = CategoryRepository(db_session)
        user_repo = UserRepository(db_session)

        category = await category_repo.create(CategoryCreate(name="Test Category"))
        user = await user_repo.create(
            UserCreate(
                username="petowner",
                first_name="Pet",
                last_name="Owner",
                email="owner@example.com",
                password="password123",
            )
        )

        # Create pet with relationships
        repo = DBPetRepository(db_session)
        payload = PetCreate(
            name="Pet with Relations", status="available", category_id=category.id, owner_id=user.id, tags=["family"]
        )

        pet = await repo.create(payload)
        assert pet.name == "Pet with Relations"
        assert pet.category_id == category.id
        assert pet.owner_id == user.id

    async def test_pet_crud_operations(self, db_session: AsyncSession) -> None:
        """Test basic pet CRUD operations."""
        repo = DBPetRepository(db_session)

        # Create
        pet = await repo.create(PetCreate(name="CRUD Pet", status="available"))
        pet_id = pet.id

        # Read
        retrieved = await repo.get_db_entity(pet_id)
        assert retrieved is not None
        assert retrieved.name == "CRUD Pet"

        # Delete
        await repo.delete(pet_id)

        # Verify deletion raises exception
        with pytest.raises(EntityNotFoundException):
            await repo.get_db_entity(pet_id)


class TestPetService:
    """Test PetService business logic."""

    async def test_service_create_pet_with_tag_creation(self, db_session: AsyncSession) -> None:
        """Test service layer creates tags automatically."""
        # Setup repositories
        pet_repo = DBPetRepository(db_session)
        tag_repo = TagRepository(db_session)
        category_repo = CategoryRepository(db_session)
        user_repo = UserRepository(db_session)

        service = PetService(pet_repo, tag_repo, category_repo, user_repo)

        # Create pet with new tags
        payload = PetCreate(name="Service Pet", status="available", tags=["auto_created_tag1", "auto_created_tag2"])

        pet = await service.create(payload)
        assert pet.name == "Service Pet"
        assert sorted(pet.tags) == ["auto_created_tag1", "auto_created_tag2"]

        # Verify tags were created in repository
        all_tags = await tag_repo.ensure_exist_by_names(["auto_created_tag1", "auto_created_tag2"])
        assert len(all_tags) == 2


class TestRepositoryExceptionHandling:
    """Test exception handling in repository layer."""

    async def test_duplicate_entity_in_repository(self, db_session: AsyncSession) -> None:
        """Test that duplicate entity creation raises DuplicateEntityException."""
        repo = CategoryRepository(db_session)

        # Create first category
        payload = CategoryCreate(name="Unique Category")
        await repo.create(payload)

        # Try to create duplicate - should raise DuplicateEntityException
        with pytest.raises(DuplicateEntityException) as exc_info:
            await repo.create(payload)

        exception = exc_info.value
        assert exception.entity_type == "CategoryEntity"
        assert exception.field == "name"
        assert "already exists" in str(exception)

    async def test_foreign_key_violation_in_repository(self, db_session: AsyncSession) -> None:
        """Test that foreign key violations raise ForeignKeyViolationException."""
        repo = DBPetRepository(db_session)

        # Try to create pet with non-existent category
        payload = PetCreate(name="Test Pet", status="available", category_id="non-existent-category-id")

        with pytest.raises(ForeignKeyViolationException) as exc_info:
            await repo.create(payload)

        exception = exc_info.value
        assert exception.field == "category_id"
        assert exception.value == "non-existent-category-id"
        assert exception.referenced_entity == "CategoryEntity"
