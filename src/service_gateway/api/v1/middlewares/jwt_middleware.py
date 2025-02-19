from uuid import UUID

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from src.service_gateway.api.v1.schemas.general.general_schemas import ResponseSchema
from src.service_gateway.security.authentication import decode_access_token

API_ROOT = "/api/v1"
PUBLIC_ROUTES = [
    "/",
    "/docs",
    "/redoc",
    "/openapi.json",
    "/auth/signin",
    "/auth/signup",
    "/auth/secure_code",
]

api_public_routes = [f"{API_ROOT}{route}" for route in PUBLIC_ROUTES]


class JWTMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path in api_public_routes:
            return await call_next(request)

        authorization: str = str(request.headers.get("Authorization"))
        if not authorization or not authorization.startswith("Bearer "):
            return JSONResponse(
                status_code=401,
                content=ResponseSchema[None](
                    msg="Token missing or invalid.", data=None
                ).model_dump(),
                headers={"WWW-Authenticate": "Bearer"},
            )

        token = authorization.split(" ")[1]

        decode_result = decode_access_token(token)

        if not decode_result.data:
            return JSONResponse(
                status_code=401,
                content=ResponseSchema[None](
                    msg=decode_result.msg, data=None
                ).model_dump(),
                headers={"WWW-Authenticate": "Bearer"},
            )

        payload = decode_result.data

        try:
            setattr(request.state, "user_id", UUID(payload["sub"]))
        except ValueError:
            return JSONResponse(
                status_code=401,
                content=ResponseSchema[None](
                    msg="Invalid token.", data=None
                ).model_dump(),
                headers={"WWW-Authenticate": "Bearer"},
            )

        return await call_next(request)
