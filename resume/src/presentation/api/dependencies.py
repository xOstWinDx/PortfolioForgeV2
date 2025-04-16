from src.application.services.profile import ProfileService
from src.application.services.project import ProjectService
from src.infrastructure.database import DEFAULT_SESSION_FACTORY
from src.infrastructure.uow import UnitOfWork


def get_profile_service() -> ProfileService:
    return ProfileService()


def get_project_service() -> ProjectService:
    return ProjectService()


def get_uow() -> UnitOfWork:
    return UnitOfWork(session_maker=DEFAULT_SESSION_FACTORY)
