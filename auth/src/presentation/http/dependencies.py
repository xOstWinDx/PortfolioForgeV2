import logging

from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer
from starlette import status
from starlette.requests import Request

from src.application.interfaces.cache import ICacheClient
from src.application.services.auth import AuthService
from src.application.services.user import UserService
from src.domain.credentials import AuthenticateCredentials, AuthorizeCredentials
from src.domain.exceptions import UnauthorizedError
from src.domain.filter import UserFilter
from src.domain.user import User
from src.infrastructure.credentials import JWTCredentialManager
from src.infrastructure.database import DEFAULT_SESSION_FACTORY
from src.infrastructure.producer import RabbitMQProducer
from src.infrastructure.s3 import S3Client
from src.infrastructure.uow import UnitOfWork

logger = logging.getLogger(__name__)


class AccessTokenBearer(HTTPBearer):
    async def __call__(self, request: Request) -> str | None:
        # 1. Проверяем куки в первую очередь
        if "access_token" in request.cookies:
            return request.cookies["access_token"]  # type: ignore
        return None


class RefreshTokenBearer(HTTPBearer):
    async def __call__(self, request: Request) -> str | None:
        # 1. Проверяем куки в первую очередь
        if "refresh_token" in request.cookies:
            return request.cookies["refresh_token"]  # type: ignore
        return None


class CredentialsBearer(AccessTokenBearer, RefreshTokenBearer):
    async def __call__(  # type: ignore
        self, request: Request
    ) -> tuple[AuthenticateCredentials, AuthorizeCredentials]:
        access = await AccessTokenBearer.__call__(self, request)
        refresh = await RefreshTokenBearer.__call__(self, request)

        return AuthenticateCredentials(access), AuthorizeCredentials(refresh)


credentials_schema = CredentialsBearer(auto_error=False)


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


async def get_current_user(
    credentials: tuple[AuthenticateCredentials, AuthorizeCredentials] = Depends(
        credentials_schema
    ),
    uow: UnitOfWork = Depends(get_uow),
    credentials_manager: JWTCredentialManager = Depends(get_credential_manager),
) -> User:
    try:
        base_user = credentials_manager.decode_credentials(credentials[0])
    except UnauthorizedError:
        try:
            base_user = credentials_manager.decode_credentials(credentials[1])
        except UnauthorizedError as e:
            logger.warning(e)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized"
            )
    async with uow:
        user = await uow.users.get(UserFilter(id=base_user.id))
    if not isinstance(user, User):
        raise UnauthorizedError("User not found")
    return user


async def get_s3_client() -> S3Client:
    return S3Client()
