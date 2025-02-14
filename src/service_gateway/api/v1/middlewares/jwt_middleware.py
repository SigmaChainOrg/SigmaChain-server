from uuid import UUID

from starlette.authentication import (
    AuthCredentials,
    AuthenticationBackend,
    AuthenticationError,
)

from src.service_gateway.security.authentication import decode_access_token

API_ROOT = "/api/v1"
PUBLIC_ROUTES = ["", "/docs", "/redoc", "/openapi.json", "/auth/signin", "/auth/signup"]

api_public_routes = [f"{API_ROOT}{route}" for route in PUBLIC_ROUTES]


class JWTAuthBackend(AuthenticationBackend):
    async def authenticate(self, conn):
        if conn.url.path in api_public_routes:
            return None

        auth_header = conn.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise AuthenticationError("Missing or invalid Authorization header")

        token = auth_header.split(" ")[1]

        decode_result = decode_access_token(token)

        if not decode_result.data:
            raise AuthenticationError(decode_result.msg)

        payload = decode_result.data

        return AuthCredentials(["authenticated"]), UUID(payload["sub"])
