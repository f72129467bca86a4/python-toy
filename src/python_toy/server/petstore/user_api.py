from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query, Request
from fastapi_utils.cbv import cbv
from starlette.status import HTTP_201_CREATED

from python_toy.server.model.common import EmptyResponse, PageResponse
from .user_service import UserService
from .models import User, UserCreate
from python_toy.server.petstore.id_type import UserId


router = APIRouter(tags=["users"])


def _service_dep(request: Request) -> UserService:
    from python_toy.server.infra.container import Container

    container: Container = request.app.state.container
    return container.user_service()


@cbv(router)
class UserRoutes:
    _service: UserService = Depends(_service_dep)

    @router.post("/v1/users", status_code=HTTP_201_CREATED)
    async def create(self, payload: UserCreate) -> User:
        return await self._service.create(payload)

    @router.get("/v1/users")
    async def list(
        self,
        page: Annotated[int, Query(ge=1)] = 1,
        size: Annotated[int, Query(ge=1, le=100)] = 10,
    ) -> PageResponse[User]:
        return await self._service.list(page, size)

    @router.get("/v1/users/{user_id}")
    async def get(self, user_id: UserId) -> User:
        return await self._service.get(user_id)

    @router.delete("/v1/users/{user_id}")
    async def delete(self, user_id: UserId) -> EmptyResponse:
        await self._service.delete(user_id)
        return EmptyResponse()


__all__ = ("router",)
