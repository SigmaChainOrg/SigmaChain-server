from uuid import UUID

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from src.service_gateway.security.authentication import decode_access_token
from src.utils.http_exceptions import AuthenticationError

API_ROOT = "/api/v1"
PUBLIC_ROUTES = [
    "/",
    "/docs",
    "/redoc",
    "/openapi.json",
    "/auth/signin",
    "/auth/signup",
]

api_public_routes = [f"{API_ROOT}{route}" for route in PUBLIC_ROUTES]


class JWTMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path in api_public_routes:
            return await call_next(request)

        authorization: str = str(request.headers.get("Authorization"))
        if not authorization or not authorization.startswith("Bearer "):
            raise AuthenticationError("Token missing or invalid")

        token = authorization.split(" ")[1]

        decode_result = decode_access_token(token)

        if not decode_result.data:
            raise AuthenticationError(decode_result.msg)

        payload = decode_result.data

        try:
            setattr(request.state, "user_id", UUID(payload["sub"]))
        except ValueError:
            raise AuthenticationError("Invalid token.")

        return await call_next(request)
