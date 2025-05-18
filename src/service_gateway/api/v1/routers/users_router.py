from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.configuration import get_db
from src.service_gateway.api.v1.schemas.access_control.user_schemas import (
    UserFilters,
    UserQuery,
    UserRead,
)
from src.service_gateway.api.v1.schemas.general.general_schemas import (
    APIResponse,
    PaginatedData,
)
from src.service_gateway.api.v1.services.user_service import UserService

security = HTTPBearer()

users_router = APIRouter(
    prefix="/users", tags=["Users"], dependencies=[Depends(security)]
)


@users_router.get(
    "",
    response_model=APIResponse[PaginatedData[UserRead]],
    status_code=200,
)
async def get_users(
    filters: UserFilters = Depends(),
    db: AsyncSession = Depends(get_db),
):
    user_service = UserService(db)
    users_paginated = await user_service.get_users(filters)

    return JSONResponse(
        content=APIResponse[PaginatedData[UserRead]](
            msg="Users retrieved successfully",
            data=users_paginated,
            ok=True,
        ).model_dump()
    )


@users_router.get(
    "/{user_id}",
    response_model=APIResponse[UserRead],
    status_code=200,
)
async def get_user(
    user_id: UUID,
    query: UserQuery = Depends(),
    db: AsyncSession = Depends(get_db),
):
    user_service = UserService(db)
    user_squema = await user_service.get_user_data_by_id(user_id, query)

    return JSONResponse(
        content=APIResponse[UserRead](
            msg="User retrieved successfully",
            data=user_squema,
            ok=True,
        ).model_dump()
    )
