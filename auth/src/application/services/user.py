from src.application.interfaces.producer import IProducer
from src.application.interfaces.uow import AbstractUnitOfWork
from src.domain.exceptions import ConflictError
from src.domain.filter import UserFilter
from src.domain.user import User


class UserService:
    def __init__(self, uow: AbstractUnitOfWork, producer: IProducer) -> None:
        self.uow = uow
        self.producer = producer

    async def create_user(self, user_data: User) -> User:
        async with self.uow:
            if await self.uow.users.exists(UserFilter(email=user_data.email)):
                raise ConflictError(f"User with email {user_data.email} already exists")
            user = await self.uow.users.create(user_data)
            await self.producer.create_user(user)
            await self.uow.commit()
        return user

    async def update_user(self, user: User) -> User:
        async with self.uow:
            user = await self.uow.users.update(user)
            await self.uow.commit()
        return user
