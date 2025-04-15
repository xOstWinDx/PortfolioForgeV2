from src.application.interfaces.producer import IProducer
from src.application.interfaces.uow import AbstractUnitOfWork
from src.domain.exceptions import ConflictError
from src.domain.filter import UserFilter
from src.domain.user import User


class UserService:
    def __init__(self, producer: IProducer) -> None:
        self.producer = producer

    async def create_user(self, user_data: User, uow: AbstractUnitOfWork) -> User:
        if await uow.users.exists(UserFilter(email=user_data.email)):
            raise ConflictError(f"User with email {user_data.email} already exists")
        user = await uow.users.create(user_data)
        await self.producer.create_user(user)
        await uow.commit()
        return user

    async def update_user(self, user: User, uow: AbstractUnitOfWork) -> User:
        user = await uow.users.update(user)
        await uow.commit()
        await self.producer.update_user(user)
        return user
