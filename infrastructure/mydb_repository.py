import os
from typing import Generic, List, Optional, Type, TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.ports import MyDBPort
from infrastructure.db import get_engine, get_session_factory

T = TypeVar("T")

class MyDBRepository(MyDBPort[T], Generic[T]):
    def __init__(self, entity_class: Type[T]):
        self.entity_class = entity_class
        database_url = os.getenv("DATABASE_URL")
        engine = get_engine(database_url)
        session_factory = get_session_factory(engine)
        self.session: AsyncSession = session_factory()

    async def add(self, entity: T) -> T:
        self.session.add(entity)
        await self.session.flush()
        return entity

    async def get_by_id(self, entity_id: int) -> Optional[T]:
        return await self.session.get(self.entity_class, entity_id)

    async def get_all(self) -> List[T]:
        result = await self.session.execute(select(self.entity_class))
        return result.scalars().all()

    async def filter_by(self, **kwargs) -> List[T]:
        result = await self.session.execute(
            select(self.entity_class).filter_by(**kwargs)
        )
        return result.scalars().all()

    async def update(self, entity: T) -> T:
        merged = await self.session.merge(entity)
        await self.session.flush()
        return merged

    async def delete(self, entity: T) -> None:
        await self.session.delete(entity)

    async def commit(self) -> None:
        await self.session.commit()

    async def rollback(self) -> None:
        await self.session.rollback()

    async def close(self) -> None:
        """세션을 명시적으로 닫습니다."""
        await self.session.close()
