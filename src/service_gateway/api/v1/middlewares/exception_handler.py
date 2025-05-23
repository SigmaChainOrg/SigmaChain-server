from fastapi import Request
from fastapi.responses import JSONResponse

from src.service_gateway.api.v1.schemas.general.general_schemas import APIErrorResponse


async def custom_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content=APIErrorResponse(detail="Internal server error.").model_dump(),
    )
