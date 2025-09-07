from __future__ import annotations

from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Factory, Singleton

from python_toy.server.infra import config as config_module
from python_toy.server.petstore.pet_repository import DBPetRepository
from python_toy.server.petstore.pet_service import PetService
from python_toy.server.petstore.category_repository import CategoryRepository
from python_toy.server.petstore.tag_repository import TagRepository
from python_toy.server.petstore.user_repository import UserRepository
from python_toy.server.petstore.category_service import CategoryService
from python_toy.server.petstore.tag_service import TagService
from python_toy.server.petstore.user_service import UserService


class Container(DeclarativeContainer):
    # Settings are created once and reused
    settings = Singleton(config_module.get_settings)

    # Repository providers (require session parameter at call time)
    pet_repository = Factory(DBPetRepository)
    category_repository = Factory(CategoryRepository)
    tag_repository = Factory(TagRepository)
    user_repository = Factory(UserRepository)

    # Service providers with proper dependency injection
    pet_service = Factory(
        PetService,
        repo=pet_repository,
        tag_repo=tag_repository,
        category_repo=category_repository,
        user_repo=user_repository,
    )

    category_service = Factory(CategoryService)
    tag_service = Factory(TagService)
    user_service = Factory(UserService)


__all__ = ("Container",)
