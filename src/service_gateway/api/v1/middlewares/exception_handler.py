from fastapi import Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

from src.service_gateway.api.v1.schemas.general.general_schemas import ResponseSchema


async def custom_exception_handler(request: Request, exc: Exception):
    if isinstance(exc, IntegrityError):
        return JSONResponse(
            status_code=500,
            content=ResponseSchema(msg="Unique key integrity error.").model_dump(),
        )

    return JSONResponse(
        status_code=500,
        content=ResponseSchema(msg="Internal server error.").model_dump(),
    )
