from fastapi import FastAPI
from app.api.main import router

from app.core.config import settings

app = FastAPI(
    title=settings.API_TITLE,
    description=settings.API_DESCRIPTION,
    version=settings.API_VERSION,
)
app.include_router(router)


@app.get("/health")
def health():
    return {"status": "ok"}
