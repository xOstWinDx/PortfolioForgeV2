from abc import ABC, abstractmethod

from src.domain.entities.profile import Profile
from src.domain.entities.project import Project
from src.domain.filters.projects import ProjectsFilter


class IProfilesRepository(ABC):
    @abstractmethod
    async def get(self) -> Profile:
        raise NotImplementedError

    @abstractmethod
    async def update(self, profile: Profile) -> Profile:
        raise NotImplementedError


class IProjectsRepository(ABC):
    @abstractmethod
    async def get(
        self, filter: ProjectsFilter, offset: int, limit: int
    ) -> list[Project]:
        raise NotImplementedError

    @abstractmethod
    async def create(self, project: Project) -> Project:
        raise NotImplementedError
