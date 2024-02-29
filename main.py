from fastapi import FastAPI
from src.core.config.database import Base, engine

app = FastAPI()
app.title = "SigmaChain API"
app.version = "0.0.1"

Base.metadata.create_all(bind=engine)


@app.get("/", tags=["Index"])
async def index():
    return {"message": "Welcome to SigmaChain API"}
