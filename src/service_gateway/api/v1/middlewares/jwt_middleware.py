from uuid import UUID

from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute
from starlette.middleware.base import BaseHTTPMiddleware

from src.service_gateway.api.v1.routers.auth_router import auth_router_open
from src.service_gateway.api.v1.schemas.general.general_schemas import APIErrorResponse
from src.service_gateway.security.authentication import decode_access_token

API_ROOT = "/api/v1"
PUBLIC_ROUTES = [
    "/",
    "/docs",
    "/redoc",
    "/openapi.json",
]

auth_open_routes = [
    f"{API_ROOT}{route.path}"
    for route in auth_router_open.routes
    if isinstance(route, APIRoute)
]

api_public_routes = [f"{API_ROOT}{route}" for route in PUBLIC_ROUTES]
api_public_routes.extend(auth_open_routes)


class JWTMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path in api_public_routes:
            return await call_next(request)

        authorization: str = str(request.headers.get("Authorization"))
        if not authorization or not authorization.startswith("Bearer "):
            return JSONResponse(
                status_code=401,
                content=APIErrorResponse(
                    detail="Token missing or invalid."
                ).model_dump(),
                headers={"WWW-Authenticate": "Bearer"},
            )

        token = authorization.split(" ")[1]

        decode_result = decode_access_token(token)

        if not decode_result.data:
            return JSONResponse(
                status_code=401,
                content=APIErrorResponse(detail=decode_result.msg).model_dump(),
                headers={"WWW-Authenticate": "Bearer"},
            )

        payload = decode_result.data

        try:
            setattr(request.state, "user_id", UUID(payload["sub"]))
        except ValueError:
            return JSONResponse(
                status_code=401,
                content=APIErrorResponse(detail="Invalid token.").model_dump(),
                headers={"WWW-Authenticate": "Bearer"},
            )

        return await call_next(request)
