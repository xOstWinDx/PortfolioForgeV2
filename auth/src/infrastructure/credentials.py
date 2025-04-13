import logging
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta

import jwt

from src.application.interfaces.cache import ICacheClient
from src.application.interfaces.credentials import ICredentialManager
from src.config import settings
from src.domain.credentials import AuthorizeCredentials, AuthenticateCredentials
from src.domain.exceptions import UnauthorizedError
from src.domain.user import User

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class JWTAccessPayload:
    sub: int
    role: str
    exp: int
    iat: int


@dataclass(frozen=True)
class JWTRefreshPayload:
    sub: int
    exp: int
    iat: int


class JWTCredentialManager(ICredentialManager):
    def __init__(self, cache_client: ICacheClient) -> None:
        self.cache_client = cache_client

    # ────────────────
    # TODO [13.04.2025 | Medium]
    # Assigned to: stark
    # Description: Добавить работу с кешем
    # Steps:
    #   - White
    #   - black
    # ────────────────

    async def make_authorize(self, user: User) -> AuthorizeCredentials:
        exp = int(
            (
                datetime.now() + timedelta(seconds=settings.ACCESS_TOKEN_EXPIRES)
            ).timestamp()
        )
        payload = JWTAccessPayload(
            sub=user.id,
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
            sub=user.id, exp=exp, iat=int(datetime.now().timestamp())
        )
        token = jwt.encode(
            payload=asdict(payload),  # noqa
            key=settings._PRIVATE_KEY,
            algorithm=settings.ALGORITHM,
            headers={"kid": settings.CURRENT_KID},
        )
        return AuthenticateCredentials(credentials=token)

    async def renew_authorize(
        self, user: User, authenticate: AuthenticateCredentials
    ) -> tuple[AuthorizeCredentials, AuthenticateCredentials]:
        refresh = authenticate.read()
        try:
            payload = jwt.decode(
                jwt=refresh, key=settings.PUBLIC_KEY, algorithms=[settings.ALGORITHM]
            )
            if payload["sub"] != user.id:
                raise UnauthorizedError("Refresh token is invalid")

            return await self.make_authorize(user), await self.make_authenticate(user)
        except jwt.ExpiredSignatureError:
            raise UnauthorizedError("Refresh token is expired")
        except jwt.InvalidTokenError:
            raise UnauthorizedError("Refresh token is invalid")
        except Exception as e:
            logger.warning(f"Unexpected error: {e}")
            raise UnauthorizedError("Refresh token is invalid")
