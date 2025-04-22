from dataclasses import dataclass


@dataclass(frozen=True)
class Author:
    id: str  # ObjectId
    name: str
    email: str
    photo_url: str

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "photo_url": self.photo_url,
        }
