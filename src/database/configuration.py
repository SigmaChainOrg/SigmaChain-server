from typing import AsyncGenerator
from decouple import config
from decouple import UndefinedValueError
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base

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

Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        yield session
