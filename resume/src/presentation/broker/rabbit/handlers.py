import datetime
import json
from typing import Any

from aio_pika import Message

from src.application.services.profile import ProfileService
from src.application.services.project import ProjectService
from src.domain.entities.profile import Profile, JobStatus, SocialLink
from src.domain.entities.project import Project
from src.infrastructure.database import DEFAULT_SESSION_FACTORY

from src.infrastructure.uow import UnitOfWork


async def create_project(message: Message) -> None:
    payload = json.loads(message.body.decode())
    service = ProjectService()
    uow = UnitOfWork(session_maker=DEFAULT_SESSION_FACTORY)
    async with uow:
        payload.pop("created_at")
        project = Project(
            id=None,
            updated_at=datetime.datetime.now(),
            created_at=datetime.datetime.now(),
            **payload,
        )
        await service.create(project, uow)
        await uow.commit()


async def update_profile(message: Message) -> None:
    payload: dict[str, Any] = json.loads(message.body.decode())
    uow = UnitOfWork(session_maker=DEFAULT_SESSION_FACTORY)
    service = ProfileService()
    async with uow:
        profile = Profile(
            updated_at=datetime.datetime.now(),
            job_status=JobStatus(payload.pop("job_status")),
            social_links={
                SocialLink(k): v for k, v in payload.pop("social_links").items()
            },
            **payload,
        )
        await service.update_profile(profile, uow)
        await uow.commit()
