from dataclasses import dataclass
from datetime import datetime

from src.domain.author import Author


@dataclass(frozen=True)
class Post:
    id: str # ObjectID
    title: str
    content: str
    author: Author
    dislikes: int
    likes: int
    created_at: datetime
    comments_count: int
    photos: list[str]
