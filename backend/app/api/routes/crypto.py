from typing import Annotated

from fastapi import APIRouter, Form

from app.crud import crypto as crypto_crud
from app.deps.auth import SessionDep, CurrentUser
from app.i18n import _
from app.schemas.users import UserKeyCreate, UserKeyPublic
from app.schemas.utils import HTTPError, add_responses

router = APIRouter(prefix="/crypto", tags=["crypto"])


@router.post("/user/keys/", response_model=UserKeyPublic)
async def save_user_keys(
    session: SessionDep,
    keys: Annotated[UserKeyCreate, Form()],
) -> UserKeyPublic:
    user_keys = await crypto_crud.create_user_key(session=session, keys_create=keys)
    return user_keys


@router.get("/users/keys/", response_model=UserKeyPublic, responses=add_responses(404))
async def get_user_keys(
    session: SessionDep, current_user: CurrentUser
) -> UserKeyPublic:
    keys = await crypto_crud.get_user_key(session=session, user_id=current_user.id)
    if keys is None:
        raise HTTPError(status_code=404, msg=_("No keys found for this user"))
    return keys
