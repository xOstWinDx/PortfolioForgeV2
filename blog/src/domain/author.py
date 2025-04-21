from dataclasses import dataclass


@dataclass(frozen=True)
class Author:
    id: str  # ObjectId
    name: str
    email: str
    photo_url: str

