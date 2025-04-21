import json
from typing import Any, Literal

import aio_pika
from aio_pika import Message
from aio_pika.abc import AbstractRobustConnection

from src.config import settings
from src.schemas.resume import ProfileSchema, ProjectSchema


class Producer:
    connection: AbstractRobustConnection | None = None

    async def update_profile(self, profile: ProfileSchema) -> None:
        return await self._produce_resume(
            "update_profile", profile.model_dump(mode="json")
        )

    async def create_project(self, project: ProjectSchema) -> None:
        return await self._produce_resume(
            "create_project", project.model_dump(mode="json")
        )

    async def _produce_resume(
        self, type: Literal["create_project", "update_profile"], msg: dict[str, Any]
    ) -> None:
        if self.connection is None:
            self.connection = await aio_pika.connect_robust(
                settings.RABBITMQ_URL, timeout=10
            )
        async with self.connection.channel() as channel:
            await channel.default_exchange.publish(
                Message(body=json.dumps(msg, ensure_ascii=False).encode(), type=type),
                routing_key="resume",
            )
