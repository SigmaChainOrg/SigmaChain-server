from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

from src.service_gateway.api.v1.middlewares.exception_handler import (
    custom_exception_handler,
)
from src.service_gateway.api.v1.middlewares.jwt_middleware import JWTMiddleware
from src.service_gateway.api.v1.routers.main_router import api_v1_router
from src.service_gateway.api.v1.schemas.general.general_schemas import ResponseSchema

api_v1 = FastAPI()
api_v1.title = "SigmaChain API v1"
api_v1.version = "0.0.2"


# Adding Middlewares
api_v1.add_middleware(JWTMiddleware)

# Adding Exception Handlers
api_v1.add_exception_handler(Exception, custom_exception_handler)


@api_v1.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content=ResponseSchema(msg=exc.detail).model_dump(),
    )


# Mounting routers
api_v1.include_router(api_v1_router)
