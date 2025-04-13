from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from src.application.interfaces.uow import AbstractUnitOfWork
from src.infrastructure.repo import SQLUserRepository


class UnitOfWork(AbstractUnitOfWork):
    def __init__(self, session_maker: async_sessionmaker[AsyncSession]) -> None:
        self.session_maker = session_maker
        self.session: None | AsyncSession = None

    @property
    def users(self) -> SQLUserRepository:
        assert self.session, "aenter() must be called first"
        return SQLUserRepository(self.session)

    async def commit(self) -> None:
        await self.session.commit()  # type: ignore[union-attr]

    async def rollback(self) -> None:
        await self.session.rollback()  # type: ignore[union-attr]

    async def close(self) -> None:
        await self.session.close()  # type: ignore[union-attr]

    async def __aenter__(self) -> None:
        session = self.session_maker()
        self.session = await session.__aenter__()
