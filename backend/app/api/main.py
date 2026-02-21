from fastapi import APIRouter
from app.api.routes import celery, users, login, storage

router = APIRouter()

router.include_router(login.router)
router.include_router(users.router)
router.include_router(celery.router)
router.include_router(storage.router)
