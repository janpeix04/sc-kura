from typing import Annotated
from fastapi import Depends


from sqlmodel.ext.asyncio.session import AsyncSession
from app.core.database import get_session

from app.schemas.users import UserBase, UserRegisterForm
from app.schemas.uitls import error_codes, HTTPError
from app.crud import auth as auth_crud

SessionDep = Annotated[AsyncSession, Depends(get_session)]


@error_codes(409)
async def validate_user(session: SessionDep, user_in: UserBase) -> UserBase:
    existing_user = await auth_crud.get_user_by_email(
        session=session, email=user_in.email
    )
    if existing_user:
        raise HTTPError(
            status_code=409,
            msg="User with this email already exists",
            loc="email",
        )
    return user_in


@error_codes(409)
async def validate_user_register_form(
    session: SessionDep,
    user_in: Annotated[UserRegisterForm, Depends(UserRegisterForm.as_form)],
) -> UserRegisterForm:
    return await validate_user(session, user_in)


ValidatedUserRegisterForm = Annotated[
    UserRegisterForm, Depends(validate_user_register_form)
]
