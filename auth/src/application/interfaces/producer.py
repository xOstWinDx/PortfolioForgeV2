from abc import ABC, abstractmethod

from src.domain.user import User


class IProducer(ABC):
    @abstractmethod
    async def create_user(self, user: User) -> None:
        """Публикует ивент создания пользователя"""
        raise NotImplementedError
