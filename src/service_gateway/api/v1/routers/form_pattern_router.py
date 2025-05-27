from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.configuration import get_db
from src.service_gateway.api.v1.schemas.general.general_schemas import APIResponse
from src.service_gateway.api.v1.schemas.workflow.form_pattern_schemas import (
    FormPatternRead,
    FormPatternUpdate,
)
from src.service_gateway.api.v1.services.form_pattern_service import FormPatternService

security = HTTPBearer()

form_pattern_router = APIRouter(
    prefix="/form-patterns",
    tags=["Form Patterns"],
    dependencies=[Depends(security)],
)


@form_pattern_router.get(
    "/{form_pattern_id}",
    response_model=APIResponse[FormPatternRead],
    status_code=200,
)
async def get_form_pattern(
    form_pattern_id: int,
    db: AsyncSession = Depends(get_db),
):
    form_pattern_service = FormPatternService(db)
    form_pattern = await form_pattern_service.get_form_pattern(form_pattern_id)

    return JSONResponse(
        content=APIResponse[FormPatternRead](
            msg="Form pattern retrieved successfully",
            data=form_pattern,
            ok=True,
        ).model_dump()
    )


@form_pattern_router.patch(
    "/{form_pattern_id}",
    response_model=APIResponse[FormPatternRead],
    status_code=200,
)
async def update_form_pattern(
    form_pattern_id: int,
    form_pattern_update: FormPatternUpdate,
    db: AsyncSession = Depends(get_db),
):
    form_pattern_service = FormPatternService(db)
    updated_form_pattern = await form_pattern_service.update_form_pattern(
        form_pattern_id, form_pattern_update
    )

    return JSONResponse(
        content=APIResponse[FormPatternRead](
            msg="Form pattern updated successfully",
            data=updated_form_pattern,
            ok=True,
        ).model_dump()
    )
