from fastapi import Depends
from starlette.requests import Request

from src.application.interfaces.cache import ICacheClient
from src.application.services.auth import AuthService
from src.application.services.user import UserService
from src.infrastructure.credentials import JWTCredentialManager
from src.infrastructure.database import DEFAULT_SESSION_FACTORY
from src.infrastructure.producer import RabbitMQProducer
from src.infrastructure.uow import UnitOfWork


async def get_uow() -> UnitOfWork:
    return UnitOfWork(session_maker=DEFAULT_SESSION_FACTORY)


def get_credential_manager() -> JWTCredentialManager:
    return JWTCredentialManager(cache_client=ICacheClient())


async def get_producer(request: Request) -> RabbitMQProducer:
    if request.app.state.connection is None:
        raise RuntimeError("Connection is not initialized")
    return RabbitMQProducer(connection=request.app.state.connection)


async def get_user_service(
    uow: UnitOfWork = Depends(get_uow),
    producer: RabbitMQProducer = Depends(get_producer),
) -> UserService:
    return UserService(uow, producer)


async def get_auth_service(
    uow: UnitOfWork = Depends(get_uow),
    credential_manager: JWTCredentialManager = Depends(get_credential_manager),
) -> AuthService:
    return AuthService(uow, credential_manager=credential_manager)
