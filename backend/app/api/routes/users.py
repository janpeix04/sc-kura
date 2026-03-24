from fastapi import APIRouter

from app.deps.auth import CurrentUser
from app.schemas.users import UserPublic

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me/", response_model=UserPublic)
async def get_user_me(current_user: CurrentUser) -> UserPublic:
    return current_user
