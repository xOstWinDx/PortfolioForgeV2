import logging
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta

import jwt

from src.application.interfaces.cache import ICacheClient
from src.application.interfaces.credentials import ICredentialManager
from src.config import settings
from src.domain.credentials import AuthorizeCredentials, AuthenticateCredentials
from src.domain.exceptions import AuthenticationError
from src.domain.user import User, RolesEnum, Avatar

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class JWTAccessPayload:
    sub: str
    role: str
    exp: int
    iat: int


@dataclass(frozen=True)
class JWTRefreshPayload:
    sub: str
    exp: int
    iat: int


class JWTCredentialManager(ICredentialManager):
    def __init__(self, cache_client: ICacheClient) -> None:
        self.cache_client = cache_client


    async def make_authorize(self, user: User) -> AuthorizeCredentials:
        exp = int(
            (
                datetime.now() + timedelta(seconds=settings.ACCESS_TOKEN_EXPIRES)
            ).timestamp()
        )
        payload = JWTAccessPayload(
            sub=str(user.id),
            role=user.role.value,
            exp=exp,
            iat=int(datetime.now().timestamp()),
        )
        token = jwt.encode(
            payload=asdict(payload),  # noqa
            key=settings._PRIVATE_KEY,
            algorithm=settings.ALGORITHM,
            headers={"kid": settings.CURRENT_KID},
        )
        return AuthorizeCredentials(credentials=token)

    async def make_authenticate(self, user: User) -> AuthenticateCredentials:
        exp = int(
            (
                datetime.now() + timedelta(seconds=settings.REFRESH_TOKEN_EXPIRES)
            ).timestamp()
        )
        payload = JWTRefreshPayload(
            sub=str(user.id), exp=exp, iat=int(datetime.now().timestamp())
        )
        token = jwt.encode(
            payload=asdict(payload),  # noqa
            key=settings._PRIVATE_KEY,
            algorithm=settings.ALGORITHM,
            headers={"kid": settings.CURRENT_KID},
        )
        return AuthenticateCredentials(credentials=token)

    async def renew_authorize(
        self, user: User, authenticate_id: str | None = None
    ) -> tuple[AuthorizeCredentials, AuthenticateCredentials]:
        return await self.make_authorize(user), await self.make_authenticate(user)

    def decode_credentials(
        self, credentials: AuthorizeCredentials | AuthenticateCredentials
    ) -> User:
        try:
            payload = jwt.decode(
                jwt=credentials.read(),
                key=settings.PUBLIC_KEY,
                algorithms=[settings.ALGORITHM],
            )
            return User(
                id=int(payload["sub"]),
                email="",
                username="",
                role=RolesEnum(payload["role"])
                if "role" in payload
                else RolesEnum.USER,
                password="",
                avatar=Avatar(id="", file_url=""),
            )
        except jwt.ExpiredSignatureError:
            raise AuthenticationError("Token is expired")
        except jwt.InvalidTokenError as e:
            raise AuthenticationError(f"Token is invalid {e}")
        except Exception as e:
            logger.warning(f"Unexpected error: {e}")
            raise e
