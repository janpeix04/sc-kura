from typing import Annotated
from fastapi import APIRouter, Form

from app.deps.auth import ValidatedUserRegisterForm, validate_user
from app.schemas.users import UserCreate, UserPublic, UserUpdateMe, UpdatePassword
from app.deps.auth import SessionDep, CurrentUser, ActiveUser
from app.crud import auth as auth_crud
from app.core.security import get_password_hash, verify_password
from app.schemas.uitls import HTTPError, add_responses

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/signup/")
async def register_user(session: SessionDep, user_in: ValidatedUserRegisterForm) -> str:
    """
    Register a new User
    """
    user_create = UserCreate.model_validate(user_in)
    await auth_crud.create_user(session=session, user_create=user_create)
    return (
        "A verification email has been sent. "
        "Please verify your email to continue. "
        "Don't forget to check your spam or junk folder."
    )


@router.patch("/me/", response_model=UserPublic)
async def update_user_me(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    user_in: Annotated[UserUpdateMe, Form()],
):
    """
    Update own user
    """
    if user_in.email:
        await validate_user(session=session, user_in=user_in)
    current_user = await auth_crud.update_user_me(
        session=session, db_user=current_user, user_in=user_in
    )
    return current_user


@router.patch("/me/password/", responses=add_responses(400))
async def update_password_me(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    body: Annotated[UpdatePassword, Form()],
) -> str:
    """
    Update own password.
    """
    if not verify_password(body.current_password, current_user.hashed_password):
        raise HTTPError(status_code=400, msg="Incorrect password")
    if body.current_password == body.new_password:
        raise HTTPError(
            status_code=400,
            msg="New password cannot be the same as the current one",
        )
    hashed_password = get_password_hash(body.new_password)
    current_user.hashed_password = hashed_password
    await auth_crud.update_password_me(session=session, db_user=current_user)
    return "Password updated successfully"


@router.get("/me/", response_model=UserPublic)
async def read_user_me(current_user: CurrentUser):
    """
    Get current user.
    """
    return current_user


@router.delete("/me/")
async def delete_user_me(session: SessionDep, current_user: ActiveUser) -> str:
    """
    Delete own user.
    """
    await auth_crud.delete_user(session=session, db_user=current_user)
    return "User deleted successfully"
