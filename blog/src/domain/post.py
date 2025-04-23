from dataclasses import dataclass
from datetime import datetime
from typing import Mapping, Any, Optional

from src.domain.author import Author


@dataclass
class Post:
    id: str  # ObjectID
    title: str
    content: str
    author: Optional[Author]  # В момент создания поста нет полных данных автора.
    dislikes: int
    likes: int
    created_at: datetime
    comments_count: int
    images: list[str]

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "Post":
        _id = data.get("id") or data.get("_id")
        return cls(
            id=str(_id),
            title=str(data.get("title")),
            content=str(data.get("content")),
            author=data.get("author"),
            dislikes=len(data.get("dislikes", [])),
            likes=len(data.get("likes", [])),
            created_at=data.get("created_at"),  # type: ignore
            comments_count=int(data.get("comments_count", 0)),
            images=list(data.get("images", [])),
        )
