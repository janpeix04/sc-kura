from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.main import router

from app.core.config import settings

app = FastAPI(
    title=settings.API_TITLE,
    description=settings.API_DESCRIPTION,
    version=settings.API_VERSION,
)
app.include_router(router, prefix=settings.API_PREFIX)

origins = [
    f"http://localhost:{settings.FRONTEND_PORT}",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health/")
def health():
    return {"status": "ok"}
