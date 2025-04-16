from src.application.interfaces.uow import AbstractUnitOfWork
from src.domain.entities.profile import Profile


class ProfileService:
    @staticmethod
    async def update_profile(profile: Profile, uow: AbstractUnitOfWork) -> Profile:
        return await uow.profiles.update(profile)

    @staticmethod
    async def get_profile(uow: AbstractUnitOfWork) -> Profile:
        return await uow.profiles.get()
