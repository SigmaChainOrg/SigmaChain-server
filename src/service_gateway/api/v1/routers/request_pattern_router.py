from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.configuration import get_db
from src.service_gateway.api.v1.schemas.general.general_schemas import APIResponse
from src.service_gateway.api.v1.schemas.workflow.activity_fields_shemas import (
    ActivityFieldsInput,
    ActivityFieldsRead,
)
from src.service_gateway.api.v1.schemas.workflow.form_pattern_schemas import (
    FormPatternInput,
    FormPatternRead,
)
from src.service_gateway.api.v1.schemas.workflow.request_pattern_schemas import (
    RequestPatternFilters,
    RequestPatternInput,
    RequestPatternQuery,
    RequestPatternRead,
    RequestPatternUpdate,
)
from src.service_gateway.api.v1.services.request_pattern_service import (
    RequestPatternService,
)

security = HTTPBearer()

request_pattern_router = APIRouter(
    prefix="/request-patterns",
    tags=["Request Patterns"],
    dependencies=[Depends(security)],
)


@request_pattern_router.get(
    "",
    response_model=APIResponse[List[RequestPatternRead]],
    status_code=200,
)
async def get_request_patterns(
    filters: RequestPatternFilters = Depends(),
    db: AsyncSession = Depends(get_db),
):
    request_pattern_service = RequestPatternService(db)
    request_patterns = await request_pattern_service.get_request_patterns(filters)

    return JSONResponse(
        content=APIResponse[List[RequestPatternRead]](
            msg="Request patterns retrieved successfully",
            data=request_patterns,
            ok=True,
        ).model_dump()
    )


@request_pattern_router.get(
    "/{request_pattern_id}",
    response_model=APIResponse[RequestPatternRead],
    status_code=200,
)
async def get_request_pattern(
    request_pattern_id: UUID,
    query: RequestPatternQuery = Depends(),
    db: AsyncSession = Depends(get_db),
):
    request_pattern_service = RequestPatternService(db)
    request_pattern = await request_pattern_service.get_request_pattern(
        request_pattern_id, query
    )

    return JSONResponse(
        content=APIResponse[RequestPatternRead](
            msg="Request pattern retrieved successfully",
            data=request_pattern,
            ok=True,
        ).model_dump()
    )


@request_pattern_router.post(
    "",
    response_model=APIResponse[RequestPatternRead],
    status_code=200,
)
async def create_request_pattern(
    input: RequestPatternInput,
    db: AsyncSession = Depends(get_db),
):
    request_pattern_service = RequestPatternService(db)
    request_pattern = await request_pattern_service.create_request_pattern(input)

    return JSONResponse(
        content=APIResponse[RequestPatternRead](
            msg="Request pattern created successfully",
            data=request_pattern,
            ok=True,
        ).model_dump()
    )


@request_pattern_router.patch(
    "/{request_pattern_id}",
    response_model=APIResponse[RequestPatternRead],
    status_code=200,
)
async def update_request_pattern(
    request_pattern_id: UUID,
    update: RequestPatternUpdate,
    db: AsyncSession = Depends(get_db),
):
    request_pattern_service = RequestPatternService(db)
    request_pattern = await request_pattern_service.update_request_pattern(
        request_pattern_id, update
    )

    return JSONResponse(
        content=APIResponse[RequestPatternRead](
            msg="Request pattern updated successfully",
            data=request_pattern,
            ok=True,
        ).model_dump()
    )


@request_pattern_router.post(
    "/{request_pattern_id}/activities/{activity_id}/form-pattern",
    response_model=APIResponse[FormPatternRead],
    status_code=200,
)
async def create_form_pattern_for_activity(
    request_pattern_id: UUID,
    activity_id: int,
    input: FormPatternInput,
    db: AsyncSession = Depends(get_db),
):
    request_pattern_service = RequestPatternService(db)
    form_pattern = await request_pattern_service.create_form_pattern_for_activity(
        request_pattern_id, activity_id, input
    )

    return JSONResponse(
        content=APIResponse[FormPatternRead](
            msg="Form pattern created successfully",
            data=form_pattern,
            ok=True,
        ).model_dump()
    )


@request_pattern_router.get(
    "/{request_pattern_id}/activities/{activity_id}/fields",
    response_model=APIResponse[List[ActivityFieldsRead]],
    status_code=200,
)
async def get_request_pattern_activity_fields(
    request_pattern_id: UUID,
    activity_id: int,
    db: AsyncSession = Depends(get_db),
):
    request_pattern_service = RequestPatternService(db)

    activity_fields = await request_pattern_service.get_request_pattern_activity_fields(
        request_pattern_id, activity_id
    )

    return JSONResponse(
        content=APIResponse[List[ActivityFieldsRead]](
            msg="Activity fields retrieved successfully",
            data=activity_fields,
            ok=True,
        ).model_dump()
    )


@request_pattern_router.put(
    "/{request_pattern_id}/activities/{activity_id}/fields",
    response_model=APIResponse[None],
    status_code=200,
)
async def put_request_pattern_activity_fields(
    request_pattern_id: UUID,
    activity_id: int,
    input: ActivityFieldsInput,
    db: AsyncSession = Depends(get_db),
):
    request_pattern_service = RequestPatternService(db)
    await request_pattern_service.put_request_pattern_activity_fields(
        request_pattern_id, activity_id, input
    )

    return JSONResponse(
        content=APIResponse[None](
            msg="Activity fields updated successfully",
            data=None,
            ok=True,
        ).model_dump()
    )


@request_pattern_router.post(
    "/{request_pattern_id}/publish",
    response_model=APIResponse[None],
    status_code=200,
)
async def publish_request_pattern(
    request_pattern_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    request_pattern_service = RequestPatternService(db)
    await request_pattern_service.publish_request_pattern(request_pattern_id)

    return JSONResponse(
        content=APIResponse[None](
            msg="Request pattern published successfully",
            data=None,
            ok=True,
        ).model_dump()
    )
