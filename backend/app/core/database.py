from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    create_async_engine,
)
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.config import settings
from app.crud import auth as auth_crud, storage as storage_crud
from app.schemas.users import UserCreate
from app.schemas.storage import FolderCreate

async_engine = create_async_engine(
    settings.DATABASE_URL,
    pool_size=10,
    max_overflow=10,
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async_session = async_sessionmaker(
        bind=async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    async with async_session() as session:
        yield session


async def init_db(session: AsyncSession) -> None:
    if settings.DEBUG:
        user = await auth_crud.get_user_by_email(
            session=session, email=settings.OWNER_EMAIL
        )
        if not user:
            user_create = UserCreate(
                username=settings.OWNER_USERNAME,
                email=settings.OWNER_EMAIL,
                password=settings.OWNER_PASSWORD,
                is_verified=True,
            )
            user = await auth_crud.create_user(session=session, user_create=user_create)

    folder = await storage_crud.get_folder_by_path(session=session, path="/")
    if not folder:
        storage_root_folder_create = FolderCreate(
            original_name="/", stored_name="/", path="/"
        )
        folder = await storage_crud.create_folder(
            session=session, folder_create=storage_root_folder_create
        )
