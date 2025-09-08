from __future__ import annotations

from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Singleton, Factory

from python_toy.server.infra import config as config_module
from python_toy.server.infra import database
from python_toy.server.infra.session_context import get_current_session
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

    # Database infrastructure
    db_engine = Singleton(database.create_database_engine, settings=settings)
    db_session_factory = Singleton(database.create_session_factory, engine=db_engine)

    # Session supplier factory that returns get_current_session
    session_supplier = Factory(lambda: get_current_session)

    # Repository providers as singletons with session supplier
    pet_repository = Singleton(DBPetRepository, session_supplier=session_supplier)
    category_repository = Singleton(CategoryRepository, session_supplier=session_supplier)
    tag_repository = Singleton(TagRepository, session_supplier=session_supplier)
    user_repository = Singleton(UserRepository, session_supplier=session_supplier)

    # Service providers as singletons with proper dependency injection
    pet_service = Singleton(
        PetService,
        repo=pet_repository,
        tag_repo=tag_repository,
        category_repo=category_repository,
        user_repo=user_repository,
    )

    category_service = Singleton(CategoryService, repo=category_repository)
    tag_service = Singleton(TagService, repo=tag_repository)
    user_service = Singleton(UserService, repo=user_repository)


__all__ = ("Container",)
