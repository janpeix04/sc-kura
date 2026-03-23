from fastapi import FastAPI

app = FastAPI(title="Title", description="description", version="v1.0.0")


@app.get("/healthcheck/", tags=["status"])
async def health_check():
    return {"title": "title", "description": "description", "version": "v1.0.0"}
