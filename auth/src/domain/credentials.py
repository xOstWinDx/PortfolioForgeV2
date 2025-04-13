from typing import Protocol


class AuthorizeCredentials(Protocol):
    def __init__(self, credentials: str) -> None:
        self.__credentials: str = credentials  # type: ignore[attr-defined]

    def read(self) -> str:
        return self.__credentials  # type: ignore


class AuthenticateCredentials(Protocol):
    def __init__(self, credentials: str) -> None:
        self.__credentials = credentials  # type: ignore[attr-defined]

    def read(self) -> str:
        return self.__credentials  # type: ignore
