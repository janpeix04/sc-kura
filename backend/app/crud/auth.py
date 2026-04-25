import uuid
from pydantic import EmailStr

from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select

from app.models import User
from app.core.security import get_password_hash, verify_password
from app.schemas.users import UserCreate, UserUpdate


async def create_user(*, session: AsyncSession, user_create: UserCreate) -> User:
    user = User.model_validate(
        user_create, update={"hashed_password": get_password_hash(user_create.password)}
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


async def update_user(
    *, session: AsyncSession, db_user: User, user_in: UserUpdate
) -> User:
    user_data = user_in.model_dump(exclude_unset=True)
    extra_data = {}
    if "password" in user_data and user_data["password"] is not None:
        password = user_data["password"]
        hashed_password = get_password_hash(password)
        extra_data["hashed_password"] = hashed_password
    db_user.sqlmodel_update(user_data, update=extra_data)
    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)
    return db_user


async def delete_user(*, session: AsyncSession, user_id: uuid.UUID) -> None:
    db_user = await session.get(User, user_id)
    await session.delete(db_user)
    await session.commit()
    return


async def get_user_by_email(*, session: AsyncSession, email: EmailStr) -> User | None:
    stmt = select(User).where(User.email == email)
    result = await session.exec(stmt)
    return result.first()


async def authenticate_user(
    *, session: AsyncSession, email: EmailStr, password: str
) -> User | None:
    user = await get_user_by_email(session=session, email=email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


async def verify_user(*, session: AsyncSession, user: User) -> User:
    user.is_verified = True
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user
