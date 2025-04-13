from dataclasses import dataclass
from enum import Enum
from functools import total_ordering
from typing import Any


@total_ordering
class RolesEnum(Enum):
    GUEST = "GUEST"
    BAN = "BAN"
    USER = "USER"
    MODERATOR = "MODERATOR"
    ADMIN = "ADMIN"

    # Порядок для сравнения
    _order = {"GUEST": 0, "BAN": 1, "USER": 2, "MODERATOR": 3, "ADMIN": 4}

    def __lt__(self, other: Any) -> bool:
        if not isinstance(other, RolesEnum):
            return NotImplemented
        return self._order[self.value] < self._order[other.value]

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, RolesEnum):
            return NotImplemented
        return self.value == other.value  # type: ignore


@dataclass
class User:
    id: int | None
    email: str
    username: str
    role: RolesEnum
    password: bytes | str  # str может быть у пользователя, в моменте создания.

    def to_json(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "email": self.email,
            "username": self.username,
        }
