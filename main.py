from fastapi import FastAPI

app = FastAPI()
app.title = "SigmaChain API"
app.version = "0.0.1"


@app.get("/", tags=["Index"])
async def index():
    return {"message": "Welcome to SigmaChain API"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app="main:app", host="0.0.0.0", port=8080, reload=True)
