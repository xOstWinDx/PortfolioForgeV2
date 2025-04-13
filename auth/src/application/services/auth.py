import uuid

from src.application.interfaces.credentials import ICredentialManager
from src.application.interfaces.uow import AbstractUnitOfWork
from src.domain.credentials import AuthorizeCredentials, AuthenticateCredentials
from src.domain.exceptions import UnauthorizedError
from src.domain.filter import UserFilter
from src.domain.user import User
from src.infrastructure.pwd_hash import verify_password


class AuthService:
    def __init__(
        self, uow: AbstractUnitOfWork, credential_manager: ICredentialManager
    ) -> None:
        self.uow = uow
        self._credential_manager = credential_manager

    async def login(
        self, email: str, password: str
    ) -> tuple[AuthorizeCredentials, AuthenticateCredentials]:
        async with self.uow:
            user = await self.uow.users.get(UserFilter(email=email))
            if not isinstance(user, User):
                user_password = uuid.uuid4().bytes
            elif not isinstance(user.password, bytes):
                raise TypeError("User password is not bytes")
            else:
                user_password = user.password

            if verify_password(password=password, hashed_password=user_password):
                if not isinstance(user, User):
                    raise RuntimeError(
                        "User is not instance of User, but it should be..."
                    )
                access_token = await self._credential_manager.make_authorize(user)
                refresh_token = await self._credential_manager.make_authenticate(user)
                return access_token, refresh_token

            raise UnauthorizedError("Invalid Email or Password")

    async def refresh(
        self, authenticate: AuthenticateCredentials
    ) -> tuple[AuthorizeCredentials, AuthenticateCredentials]:
        user = self._credential_manager.decode_credentials(authenticate)
        return await self._credential_manager.renew_authorize(user, "")  # type: ignore
