from dataclasses import dataclass


@dataclass
class UserFilter:
    id: int | None = None
    username: str | None = None
    email: str | None = None
