from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import Session

from app.core.config import settings

sync_engine = create_engine(settings.DATABASE_URL)
get_session = sessionmaker(bind=sync_engine, expire_on_commit=False, class_=Session)
