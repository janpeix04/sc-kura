from sqlmodel import select, func
from sqlmodel.ext.asyncio.session import AsyncSession
from app.models.users import User
from app.schemas.users import UserCreate, UserUpdate
from app.core.security import get_password_hash, verify_password


async def create_user(*, session: AsyncSession, user_create: UserCreate) -> User:
    user = User.model_validate(
        user_create,
        update={
            "hashed_password": get_password_hash(user_create.password),
        },
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


async def get_user_by_email(session: AsyncSession, email: str) -> User | None:
    stmt = select(User).where(User.email == email)
    result = await session.exec(stmt)
    return result.first()


async def authenticate(
    *, session: AsyncSession, email: str, password: str
) -> User | None:
    user = await get_user_by_email(session=session, email=email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


async def get_user_by_id(session: AsyncSession, id: str) -> User | None:
    stmt = select(User).where(User.id == id)
    result = await session.exec(stmt)
    return result.first()


async def verify_user(*, session: AsyncSession, db_user: User) -> User:
    db_user.is_verified = True
    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)
    return db_user


async def update_user(
    *, session: AsyncSession, db_user: User, user_in: UserUpdate
) -> User:
    user_data = user_in.model_dump(exclude_unset=True)
    extra_data = {}
    if "password" in user_data:
        password = user_data["password"]
        hashed_password = get_password_hash(password)
        extra_data["hashed_password"] = hashed_password
    db_user.sqlmodel_update(user_data, update=extra_data)
    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)
    return db_user


async def update_user_me(
    *, session: AsyncSession, db_user: User, user_in: UserUpdate
) -> User:
    user_data = user_in.model_dump(exclude_unset=True)
    db_user.sqlmodel_update(user_data)
    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)
    return db_user


async def update_password_me(*, session: AsyncSession, db_user: User) -> None:
    session.add(db_user)
    await session.commit()
    return


async def delete_user(*, session: AsyncSession, db_user: User) -> None:
    db_user = await session.get(User, db_user.id)
    await session.delete(db_user)
    await session.commit()
    return


async def get_users(
    *, session: AsyncSession, skip: int = 0, limit: int | None = None
) -> tuple[list[User], int]:
    count_stmt = select(func.count()).select_from(User)
    count = await session.exec(count_stmt)

    stmt = select(User)
    if limit is not None:
        stmt = stmt.offset(skip).limit(limit)
    users = await session.exec(stmt)

    return users.all(), count.one()
