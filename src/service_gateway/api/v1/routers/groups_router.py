from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.configuration import get_db
from src.service_gateway.api.v1.schemas.access_control.group_schemas import (
    GroupAssignUserInput,
    GroupFilters,
    GroupInput,
    GroupQuery,
    GroupRead,
    GroupUpdate,
)
from src.service_gateway.api.v1.schemas.general.general_schemas import APIResponse
from src.service_gateway.api.v1.services.group_service import GroupService

security = HTTPBearer()

groups_router = APIRouter(
    prefix="/groups", tags=["Groups"], dependencies=[Depends(security)]
)


@groups_router.get(
    "",
    response_model=APIResponse[List[GroupRead]],
    status_code=200,
)
async def get_groups(
    filters: GroupFilters = Depends(),
    db: AsyncSession = Depends(get_db),
):
    group_service = GroupService(db)
    groups = await group_service.get_groups(filters)

    return JSONResponse(
        content=APIResponse[List[GroupRead]](
            data=groups,
            msg="Groups retrieved successfully",
            ok=True,
        ).model_dump()
    )


@groups_router.get(
    "/{group_id}",
    response_model=APIResponse[GroupRead],
    status_code=200,
)
async def get_group(
    group_id: UUID,
    query: GroupQuery = Depends(),
    db: AsyncSession = Depends(get_db),
):
    group_service = GroupService(db)
    group = await group_service.get_group(group_id, query)

    return JSONResponse(
        content=APIResponse[GroupRead](
            data=group,
            msg="Group retrieved successfully",
            ok=True,
        ).model_dump()
    )


@groups_router.post(
    "",
    response_model=APIResponse[GroupRead],
    status_code=201,
)
async def create_group(input: GroupInput, db: AsyncSession = Depends(get_db)):
    group_service = GroupService(db)
    new_group = await group_service.create_group(input)

    return JSONResponse(
        content=APIResponse[GroupRead](
            data=new_group,
            msg="Group created successfully",
            ok=True,
        ).model_dump()
    )


@groups_router.patch(
    "/{group_id}",
    response_model=APIResponse[GroupRead],
    status_code=200,
)
async def update_group(
    group_id: UUID, input: GroupUpdate, db: AsyncSession = Depends(get_db)
):
    group_service = GroupService(db)
    updated_group = await group_service.update_group(group_id, input)

    return JSONResponse(
        content=APIResponse[GroupRead](
            data=updated_group,
            msg="Group updated successfully",
            ok=True,
        ).model_dump()
    )


@groups_router.post(
    "/assign-user",
    response_model=APIResponse[GroupRead],
    status_code=200,
)
async def assign_user_to_group(
    input: GroupAssignUserInput, db: AsyncSession = Depends(get_db)
):
    group_service = GroupService(db)
    updated_group = await group_service.assign_user_to_group(input)

    return JSONResponse(
        content=APIResponse[GroupRead](
            data=updated_group,
            msg="User assigned to group successfully",
            ok=True,
        ).model_dump()
    )
