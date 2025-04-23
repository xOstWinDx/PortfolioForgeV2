from dataclasses import dataclass
from typing import Mapping, Any


@dataclass(frozen=True)
class Author:
    id: int
    name: str
    email: str
    photo_url: str

    def to_dict(self) -> Mapping[str, Any]:
        return {
            "_id": self.id,
            "name": self.name,
            "email": self.email,
            "photo_url": self.photo_url,
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, int | str]) -> "Author":
        return cls(
            id=int(data.get("_id", "")),
            name=str(data.get("name")),
            email=str(data.get("email")),
            photo_url=str(data.get("photo_url")),
        )
