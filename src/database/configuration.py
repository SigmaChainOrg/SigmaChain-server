from typing import AsyncGenerator

from decouple import UndefinedValueError, config
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, MappedAsDataclass

# Ensure all models are imported
import src.database.models  # noqa

try:
    user = config("DB_USER")
    password = config("DB_PASSWORD")
    host = config("DB_HOST")
    port = config("DB_PORT")
    database = config("DB_NAME")
except UndefinedValueError as e:
    raise RuntimeError(f"Missing database configuration: {e}")

async_engine = create_async_engine(
    "{engine}://{user}:{password}@{host}:{port}/{database}".format(
        engine="postgresql+asyncpg",
        user=user,
        password=password,
        host=host,
        port=port,
        database=database,
    ),
    future=True,
)

async_session_factory = async_sessionmaker(
    bind=async_engine,
    expire_on_commit=True,
    autoflush=True,
    autocommit=False,
)


class Base(DeclarativeBase, MappedAsDataclass):
    """Base class for all models"""


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        yield session
