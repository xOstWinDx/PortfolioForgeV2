import logging

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from starlette.requests import Request

from src.application.interfaces.cache import ICacheClient
from src.application.services.auth import AuthService
from src.application.services.image import ImageService
from src.application.services.user import UserService
from src.domain.credentials import AuthorizeCredentials
from src.domain.exceptions import AuthenticationError, AuthorizationError
from src.domain.filter import UserFilter
from src.domain.user import User
from src.infrastructure.credentials import JWTCredentialManager
from src.infrastructure.database import DEFAULT_SESSION_FACTORY
from src.infrastructure.producer import RabbitMQProducer
from src.infrastructure.s3 import S3Client
from src.infrastructure.uow import UnitOfWork
from src.presentation.http.docs.description import AUTH_HEADER_NOTE

logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/login", auto_error=False, description=AUTH_HEADER_NOTE
)


async def get_uow() -> UnitOfWork:
    return UnitOfWork(session_maker=DEFAULT_SESSION_FACTORY)


def get_credential_manager() -> JWTCredentialManager:
    return JWTCredentialManager(cache_client=ICacheClient())


async def get_producer(request: Request) -> RabbitMQProducer:
    if request.app.state.connection is None:
        raise RuntimeError("Connection is not initialized")
    return RabbitMQProducer(connection=request.app.state.connection)


async def get_user_service(
    producer: RabbitMQProducer = Depends(get_producer),
) -> UserService:
    return UserService(producer)


async def get_auth_service(
    uow: UnitOfWork = Depends(get_uow),
    credential_manager: JWTCredentialManager = Depends(get_credential_manager),
) -> AuthService:
    return AuthService(uow, credential_manager=credential_manager)


async def get_current_user(
    request: Request,
    token: str = Depends(oauth2_scheme),
    uow: UnitOfWork = Depends(get_uow),
    credential_manager: JWTCredentialManager = Depends(get_credential_manager),
) -> User:
    # Продакшен-режим: берём данные из заголовков API Gateway
    if "X-User-ID" in request.headers:
        user_id = request.headers["X-User-ID"]

        if not user_id.isdigit():
            raise AuthorizationError("User not found")

        async with uow:
            user = await uow.users.get(UserFilter(id=int(user_id)))
            if not user:
                raise AuthorizationError("User not found")
        return user

    # Локальный режим: проверяем Bearer token
    if not token:
        raise AuthenticationError("Token not found")

    try:
        user_data = credential_manager.decode_credentials(AuthorizeCredentials(token))
        async with uow:
            user = await uow.users.get(UserFilter(id=user_data.id))
            if not user:
                AuthorizationError("User not found")
        return user
    except Exception as e:
        raise AuthenticationError(f"Token is invalid {e}")


async def get_s3_client() -> S3Client:
    return S3Client()


async def get_image_service(
    s3_client: S3Client = Depends(get_s3_client),
) -> ImageService:
    return ImageService(s3_client)
