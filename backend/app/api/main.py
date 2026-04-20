from fastapi import APIRouter
from app.api.routes import auth, users, storage

router = APIRouter()

router.include_router(auth.router)
router.include_router(users.router)
router.include_router(storage.router)
