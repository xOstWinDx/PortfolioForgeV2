import asyncio
import logging

import aio_pika

from src.config import settings
from src.presentation.broker.rabbit.handlers import create_project, update_profile

EVENT_HANDLERS = {"create_project": create_project, "update_profile": update_profile}

logger = logging.getLogger(__name__)


async def consumer() -> None:
    connection = await aio_pika.connect_robust(settings.RABBITMQ_URL, timeout=10)
    async with connection.channel() as channel:
        queue = await channel.declare_queue("resume", durable=True)

        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    event = message.type
                    if event not in EVENT_HANDLERS:
                        logger.warning(f"Unknown event {event}")
                        continue
                    try:
                        await EVENT_HANDLERS[event](message)
                    except Exception as e:
                        logger.exception(e)
                        continue


def start_consumer() -> None:
    asyncio.run(consumer())
