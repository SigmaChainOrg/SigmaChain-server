from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.configuration import get_db
from src.service_gateway.api.v1.schemas.general.general_schemas import APIResponse
from src.service_gateway.api.v1.schemas.workflow.request_pattern_schemas import (
    RequestPatternInput,
    RequestPatternRead,
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
    "/{request_pattern_id}",
    response_model=APIResponse[RequestPatternRead],
    status_code=200,
)
async def get_request_pattern(
    request_pattern_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    request_pattern_service = RequestPatternService(db)
    request_pattern = await request_pattern_service.get_request_pattern(
        request_pattern_id
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
