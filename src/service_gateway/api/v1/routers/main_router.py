from fastapi import APIRouter
from fastapi.responses import JSONResponse

from src.service_gateway.api.v1.routers.auth_router import auth_router, auth_router_open
from src.service_gateway.api.v1.routers.groups_router import groups_router

api_v1_router = APIRouter()

api_v1_router.include_router(auth_router_open)
api_v1_router.include_router(auth_router)
api_v1_router.include_router(groups_router)


@api_v1_router.get("/", tags=["Index"], include_in_schema=False)
async def index():
    return JSONResponse(
        content={"message": "Welcome to SigmaChain API v1"},
        status_code=200,
    )
