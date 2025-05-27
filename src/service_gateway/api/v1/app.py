from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

from src.service_gateway.api.v1.middlewares.exception_handler import (
    custom_exception_handler,
)
from src.service_gateway.api.v1.middlewares.jwt_middleware import JWTMiddleware
from src.service_gateway.api.v1.routers.main_router import api_v1_router
from src.service_gateway.api.v1.schemas.general.general_schemas import APIErrorResponse

api_v1 = FastAPI()
api_v1.title = "SigmaChain API v1"
api_v1.version = "0.0.6"

# Adding Exception Handlers


@api_v1.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content=APIErrorResponse(detail=exc.detail).model_dump(),
        headers=exc.headers,
    )


api_v1.add_exception_handler(Exception, custom_exception_handler)

# Adding Middlewares
api_v1.add_middleware(JWTMiddleware)


# Mounting routers
api_v1.include_router(api_v1_router)
