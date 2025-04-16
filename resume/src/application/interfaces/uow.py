from abc import ABC, abstractmethod

from src.application.interfaces.repo import IProfilesRepository, IProjectsRepository


class AbstractUnitOfWork(ABC):
    @property
    @abstractmethod
    def profiles(self) -> IProfilesRepository:
        raise NotImplementedError

    @property
    @abstractmethod
    def projects(self) -> IProjectsRepository:
        raise NotImplementedError

    @abstractmethod
    async def commit(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def rollback(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def close(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def __aenter__(self) -> None:
        raise NotImplementedError

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:  # type: ignore
        try:
            if exc_type is not None:
                await self.rollback()
        finally:
            await self.close()
