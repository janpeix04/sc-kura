from fastapi import FastAPI

from app.core.config import settings
from app.schemas.utils import HealthCheck

app = FastAPI(
    title=settings.API_TITLE,
    description=settings.API_DESCRIPTION,
    version=settings.API_VERSION,
)


@app.get("/healthcheck/", response_model=HealthCheck, tags=["status"])
async def health_check():
    return {
        "title": settings.API_TITLE,
        "description": settings.API_DESCRIPTION,
        "version": settings.API_VERSION,
    }
