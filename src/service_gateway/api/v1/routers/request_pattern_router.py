from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.configuration import get_db
from src.service_gateway.api.v1.schemas.general.general_schemas import APIResponse
from src.service_gateway.api.v1.schemas.workflow.request_pattern_schemas import (
    RequestPatternInput,
)

security = HTTPBearer()

request_pattern_router = APIRouter(
    prefix="/request-patterns",
    tags=["Request Patterns"],
    dependencies=[Depends(security)],
)


@request_pattern_router.post(
    "",
    response_model=APIResponse[None],
    status_code=200,
)
async def create_request_pattern(
    input: RequestPatternInput,
    db: AsyncSession = Depends(get_db),
):
    return JSONResponse(
        content=APIResponse[None](
            msg="Request pattern created successfully",
            data=None,
            ok=True,
        ).model_dump()
    )
