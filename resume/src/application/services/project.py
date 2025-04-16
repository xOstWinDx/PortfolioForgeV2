from src.application.interfaces.uow import AbstractUnitOfWork
from src.domain.entities.project import Project
from src.domain.filters.projects import ProjectsFilter


class ProjectService:
    @staticmethod
    async def create(project: Project, uow: AbstractUnitOfWork) -> Project:
        return await uow.projects.create(project)

    @staticmethod
    async def get(
        filter: ProjectsFilter, uow: AbstractUnitOfWork, offset: int, limit: int
    ) -> list[Project]:
        return await uow.projects.get(filter, offset, limit)  # type: ignore
