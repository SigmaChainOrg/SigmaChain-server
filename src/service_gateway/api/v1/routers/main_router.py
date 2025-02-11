from fastapi import APIRouter
from fastapi.responses import JSONResponse

api_v1_router = APIRouter()


@api_v1_router.get("/", tags=["Index"], include_in_schema=False)
async def index():
    return JSONResponse(
        content={"message": "Welcome to SigmaChain API v1"},
        status_code=200,
    )
