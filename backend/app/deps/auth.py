from typing import Annotated

from fastapi import Depends, Form
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.database import get_session
from app.schemas.utils import error_codes, HTTPError
from app.schemas.users import UserBase, UserRegister
from app.crud import auth as auth_crud

SessionDep = Annotated[AsyncSession, Depends(get_session)]


@error_codes(409)
async def validate_user(session: SessionDep, user_in: UserBase) -> UserBase:
    user = await auth_crud.get_user_by_email(session=session, email=user_in.email)
    if user:
        raise HTTPError(
            status_code=409, msg="User with this email already exists", loc="email"
        )
    return user_in


async def validate_user_register_form(
    session: SessionDep, user_in: Annotated[UserRegister, Form()]
) -> UserRegister:
    return await validate_user(session=session, user_in=user_in)


ValidatedUserRegister = Annotated[UserRegister, Depends(validate_user_register_form)]
