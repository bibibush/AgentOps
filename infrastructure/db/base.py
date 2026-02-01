from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

Base = declarative_base()


def get_engine(database_url: str) -> AsyncEngine:
    return create_async_engine(database_url)


def get_session_factory(engine: AsyncEngine):
    return async_sessionmaker(autocommit=False, autoflush=False, bind=engine)
