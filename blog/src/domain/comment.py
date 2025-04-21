from dataclasses import dataclass
from datetime import datetime

from src.domain.author import Author


@dataclass(frozen=True)
class Comment:
    id: str  # ObjectId
    text: str
    author: Author
    post_id: str
    parent_id: str | None
    dislikes: int
    likes: int
    answers_count: int
    created_at: datetime
