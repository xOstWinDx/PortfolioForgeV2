from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.interfaces.repo import IProfilesRepository, IProjectsRepository
from src.domain.entities.profile import Profile
from src.domain.entities.project import Project
from src.domain.filters.projects import ProjectsFilter
from src.infrastructure.models import ProfileModel, ProjectModel


class SQLProfilesRepository(IProfilesRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get(self) -> Profile:
        query = select(ProfileModel)
        res = await self.session.execute(query)
        model = res.scalar_one()
        return model.to_domain()

    async def update(self, profile: Profile) -> Profile:
        model_profile = ProfileModel.from_domain(profile)
        await self.session.merge(model_profile)
        await self.session.flush()
        return model_profile.to_domain()


class SQLProjectsRepository(IProjectsRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get(
        self, filter: ProjectsFilter, offset: int, limit: int
    ) -> list[Project]:
        query = select(ProjectModel)
        if filter.id is not None:
            query = query.where(ProjectModel.id == filter.id)  # noqa
        if filter.is_featured is not None:
            query = query.where(ProjectModel.is_featured == filter.is_featured)  # noqa
        query = query.offset(offset).limit(limit)
        res = await self.session.execute(query)
        models = res.scalars().all()
        return [model.to_domain() for model in models]

    async def create(self, project: Project) -> Project:
        model = ProjectModel.from_domain(project)
        self.session.add(model)
        await self.session.flush()
        return model.to_domain()
