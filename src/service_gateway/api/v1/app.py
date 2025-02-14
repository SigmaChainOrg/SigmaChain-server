from fastapi import FastAPI
from starlette.middleware.authentication import AuthenticationMiddleware

from src.service_gateway.api.v1.middlewares.jwt_middleware import JWTAuthBackend
from src.service_gateway.api.v1.routers.main_router import api_v1_router

api_v1 = FastAPI()
api_v1.title = "SigmaChain API v1"
api_v1.version = "0.0.2"

api_v1.add_middleware(AuthenticationMiddleware, backend=JWTAuthBackend())

api_v1.include_router(api_v1_router)
