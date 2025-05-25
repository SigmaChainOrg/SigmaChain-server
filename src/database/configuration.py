from typing import Any, AsyncGenerator, Dict, Optional, Set

from decouple import UndefinedValueError, config
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, MappedAsDataclass, object_mapper

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
    """Base class for all models, with recursive safe to_dict()."""

    def to_dict(
        self, exclude_unloaded: bool = True, _processed: Optional[Set[int]] = None
    ) -> Dict[str, Any]:
        if _processed is None:
            _processed = set()

        instance_id = id(self)
        if instance_id in _processed:
            return {"$recursive": f"{self.__class__.__name__}#{instance_id}"}

        _processed.add(instance_id)

        mapper = object_mapper(self)
        result = {col.name: getattr(self, col.name) for col in mapper.columns}

        for rel in mapper.relationships:
            if rel.key in self.__dict__ or not exclude_unloaded:
                value = getattr(self, rel.key)

                if value is None:
                    result[rel.key] = None
                elif rel.uselist:
                    result[rel.key] = [
                        item.to_dict(exclude_unloaded, _processed) for item in value
                    ]
                else:
                    result[rel.key] = (
                        value.to_dict(exclude_unloaded, _processed) if value else None
                    )

        return result


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        yield session
