from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.service_gateway.api.v1.app import api_v1

tags_metadata = [
    {
        "name": "v1",
        "description": """
        - API version 1.
        -- V1 Complete documentation at `/api/v1/docs`
        """,
    },
]

app = FastAPI(openapi_tags=tags_metadata)
app.title = "SigmaChain API"
app.version = "0.0.3"

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mounting app versions
app.mount("/api/v1", app=api_v1, name="v1")


@app.get("/", tags=["Index"], include_in_schema=False)
async def index():
    return JSONResponse(
        content={"message": "Welcome to SigmaChain API"},
        status_code=200,
    )
