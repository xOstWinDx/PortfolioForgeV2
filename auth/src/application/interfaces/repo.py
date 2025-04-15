from abc import ABC, abstractmethod

from src.domain.filter import UserFilter
from src.domain.user import User


class IUserRepository(ABC):
    @abstractmethod
    async def create(self, user: User) -> User:
        raise NotImplementedError

    @abstractmethod
    async def exists(self, filter: UserFilter) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def get(self, filter: UserFilter) -> User | None:
        raise NotImplementedError

    @abstractmethod
    async def update(self, user: User) -> User:
        raise NotImplementedError


class IImageRepository(ABC):
    @abstractmethod
    async def create(self, id: str, file_url: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def get(self, id: str) -> str | None:
        raise NotImplementedError
