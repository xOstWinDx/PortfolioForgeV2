from sqlalchemy import select, exists
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.interfaces.repo import IUserRepository
from src.domain.filter import UserFilter
from src.domain.user import User
from src.infrastructure.models import UserModel, RoleModel


class SQLUserRepository(IUserRepository):
    model = UserModel

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, user: User) -> User:
        query = select(RoleModel).where(RoleModel.name == user.role.value)  # noqa
        res = await self.session.execute(query)
        role = res.scalar_one_or_none()
        if not role:
            role = RoleModel(name=user.role.value)
            self.session.add(role)
            await self.session.flush()

        user_model = self.model.from_domain(user, role.id)
        self.session.add(user_model)
        await self.session.flush()
        user_model.role = role
        return user_model.to_domain()

    async def exists(self, filter: UserFilter) -> bool:
        query = select(exists(self.model))
        if filter.id is not None:
            query = query.where(self.model.id == filter.id)  # noqa
        if filter.username is not None:
            query = query.where(self.model.username == filter.username)  # noqa
        if filter.email is not None:
            query = query.where(self.model.email == filter.email)  # noqa
        res = await self.session.execute(query)
        return bool(res.scalar_one_or_none())

    async def get(self, filter: UserFilter) -> User | None:
        query = select(self.model)
        if filter.id is not None:
            query = query.where(self.model.id == filter.id)  # noqa
        if filter.username is not None:
            query = query.where(self.model.username == filter.username)  # noqa
        if filter.email is not None:
            query = query.where(self.model.email == filter.email)  # noqa
        res = await self.session.execute(query)
        model: UserModel | None = res.scalar_one_or_none()
        if not model:
            return None
        return model.to_domain()
