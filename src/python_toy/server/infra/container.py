from __future__ import annotations

from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Singleton

from python_toy.server.infra import config as config_module
from python_toy.server.petstore.repository import InMemoryPetRepository
from python_toy.server.petstore.service import PetService


class Container(DeclarativeContainer):
    # Settings are created once and reused
    settings = Singleton(config_module.get_settings)

    # Domain providers
    pet_repository = Singleton(InMemoryPetRepository)
    pet_service = Singleton(PetService, repo=pet_repository)


__all__ = ("Container",)
