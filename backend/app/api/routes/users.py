from datetime import timedelta

from typing import Annotated
from fastapi import APIRouter, Form

from app.deps.auth import (
    ValidatedUserRegisterForm,
    validate_user,
    SessionDep,
    CurrentUser,
    ActiveUser,
)
from app.schemas.users import UserCreate, UserPublic, UserUpdateMe, UpdatePassword
from app.crud import auth as auth_crud, storage as storage_crud
from app.core.security import get_password_hash, verify_password, create_token
from app.schemas.utils import HTTPError, add_responses
from app.api.routes.login import router as login_router
from app.core.config import settings
from app.tasks import send_verification_email
from app.models import Folder
from app.schemas.storage import FolderCreate, FileFolderStatus

router = APIRouter(prefix="/users", tags=["users"])


def _send_new_account_email(*, user_in: ValidatedUserRegisterForm):
    verify_token_expires = timedelta(hours=settings.EMAIL_TOKEN_EXPIRE_HOURS)
    token = create_token(user_in.email, verify_token_expires)
    host = f"http://{settings.API_HOST}:{settings.FRONTEND_PORT}"
    verification_link = host + login_router.url_path_for("verify_account", token=token)
    send_verification_email.delay(
        username=user_in.username,
        email=user_in.email,
        verification_link=verification_link,
    )


async def _create_user_root_folder(session: SessionDep, user_id: str) -> Folder:
    """
    Ensure the user has a root folde ('/') after registration
    """
    root_folder = await storage_crud.get_folder_by_path(
        session=session, path="/", user_id=user_id
    )

    if root_folder:
        return root_folder

    folder_create = FolderCreate(
        original_name="/",
        stored_name="/",
        path="/",
        status=FileFolderStatus.UPLOADED,
        user_id=user_id,
        parent_id=None,
    )
    root_folder = await storage_crud.create_folder(
        session=session, folder_create=folder_create
    )
    return root_folder


@router.post("/signup/")
async def register_user(session: SessionDep, user_in: ValidatedUserRegisterForm) -> str:
    """
    Register a new User
    """
    user_create = UserCreate.model_validate(user_in)
    new_user = await auth_crud.create_user(session=session, user_create=user_create)

    await _create_user_root_folder(session=session, user_id=new_user.id)
    _send_new_account_email(user_in=user_in)
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
