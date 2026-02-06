from fastapi import APIRouter
from app.api.routes import auth, celery, users

router = APIRouter()

router.include_router(auth.router)
router.include_router(celery.router)
router.include_router(users.router)
