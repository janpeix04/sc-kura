from fastapi import APIRouter
from app.api.routes import auth, users, storage, tasks

router = APIRouter()

router.include_router(auth.router)
router.include_router(users.router)
router.include_router(storage.router)
router.include_router(tasks.router)
