from typing import Annotated

from fastapi import APIRouter, Form

from app.crud import auth as auth_crud
from app.deps.auth import CurrentUser, SessionDep
from app.schemas.users import UserPublic, UserUpdate

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me/", response_model=UserPublic)
async def get_user_me(current_user: CurrentUser) -> UserPublic:
    return current_user


@router.patch("/me/", response_model=UserPublic)
async def update_user_me(
    session: SessionDep,
    current_user: CurrentUser,
    user_in: Annotated[UserUpdate, Form()],
):
    user = await auth_crud.update_user(
        session=session, db_user=current_user, user_in=user_in
    )

    return user
