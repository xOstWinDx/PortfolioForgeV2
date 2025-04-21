from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from src.application.interfaces.uow import AbstractUnitOfWork
from src.infrastructure.repo import SQLProfilesRepository, SQLProjectsRepository


class UnitOfWork(AbstractUnitOfWork):
    def __init__(self, session_maker: async_sessionmaker[AsyncSession]) -> None:
        self.session_maker = session_maker
        self.session: None | AsyncSession = None

    @property
    def profiles(self) -> SQLProfilesRepository:
        assert self.session, "aenter() must be called first"
        return SQLProfilesRepository(self.session)

    @property
    def projects(self) -> SQLProjectsRepository:
        assert self.session, "aenter() must be called first"
        return SQLProjectsRepository(self.session)

    async def commit(self) -> None:
        await self.session.commit()  # type: ignore

    async def rollback(self) -> None:
        await self.session.rollback()  # type: ignore

    async def close(self) -> None:
        await self.session.close()  # type: ignore
        self.session = None

    async def __aenter__(self) -> None:
        session = self.session_maker()
        self.session = await session.__aenter__()
