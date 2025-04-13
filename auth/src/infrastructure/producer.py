import json
from enum import StrEnum

from aio_pika import Connection, ExchangeType, Message, DeliveryMode

from src.application.interfaces.producer import IProducer
from src.domain.user import User


class MessageTypeEnum(StrEnum):
    CREATED = "created"
    UPDATED = "updated"
    DELETED = "deleted"


class RabbitMQProducer(IProducer):
    def __init__(self, connection: Connection) -> None:
        self.connection = connection

    async def create_user(self, user: User) -> None:
        async with self.connection.channel() as channel:
            exchange = await channel.declare_exchange(
                "user_events", type=ExchangeType.FANOUT, durable=True
            )
            msg = json.dumps(user.to_json(), ensure_ascii=False).encode()
            await exchange.publish(
                message=Message(
                    body=msg,
                    type=MessageTypeEnum.CREATED,
                    delivery_mode=DeliveryMode.PERSISTENT,
                ),
                routing_key="",
            )
