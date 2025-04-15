from sqlalchemy import select, exists
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.interfaces.repo import IUserRepository, IImageRepository
from src.domain.filter import UserFilter
from src.domain.user import User
from src.infrastructure.entities.models import RoleModel, UserModel, ImageModel


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

        avatar = await self.session.merge(
            ImageModel(id=user.avatar.id, file_url=user.avatar.file_url)
        )

        user_model = self.model.from_domain(user, role.id)
        self.session.add(user_model)
        await self.session.flush()
        user_model.role = role
        user_model.avatar = avatar

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

    async def update(self, user: User) -> User:
        role = await self._get_role_by_name(user.role.value)
        image = await self._get_image_by_id(user.avatar.id)
        user_model = self.model.from_domain(user, role_id=role.id)
        user_model.role = role
        user_model.avatar = image
        await self.session.merge(user_model)
        await self.session.flush()
        return user_model.to_domain()

    async def _get_role_by_name(self, name: str) -> RoleModel:
        query = select(RoleModel).where(RoleModel.name == name)  # noqa
        res = await self.session.execute(query)
        role = res.scalar_one_or_none()
        return role

    async def _get_image_by_id(self, id: str) -> ImageModel | None:
        query = select(ImageModel).where(ImageModel.id == id)  # noqa
        res = await self.session.execute(query)
        image = res.scalar_one_or_none()
        return image


class SQLImageRepository(IImageRepository):
    model = ImageModel

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, id: str, file_url: str) -> bool:
        image = ImageModel(id=id, file_url=file_url)
        self.session.add(image)
        await self.session.flush()
        return True

    async def get(self, id: str) -> str | None:
        image = await self.session.get(self.model, id)
        return image.file_url if image else None
