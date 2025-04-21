from abc import ABC, abstractmethod

from src.domain.credentials import AuthorizeCredentials, AuthenticateCredentials
from src.domain.user import User


class ICredentialManager(ABC):
    @abstractmethod
    async def make_authorize(self, user: User) -> AuthorizeCredentials:
        raise NotImplementedError

    @abstractmethod
    async def make_authenticate(self, user: User) -> AuthenticateCredentials:
        raise NotImplementedError

    @abstractmethod
    async def renew_authorize(
        self, user: User, authenticate_id: str | None = None
    ) -> tuple[AuthorizeCredentials, AuthenticateCredentials]:
        raise NotImplementedError

    @abstractmethod
    def decode_credentials(
        self, credentials: AuthorizeCredentials | AuthenticateCredentials
    ) -> User:
        raise NotImplementedError
