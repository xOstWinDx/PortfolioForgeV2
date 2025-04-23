from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Mapping, Any

from src.domain.author import Author


@dataclass
class Comment:
    id: str  # ObjectId
    text: str
    author: Optional[Author]  # Может быть None в моменте создания.
    post_id: str
    parent_id: str | None
    dislikes: int
    likes: int
    answers_count: int
    created_at: datetime

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "Comment":
        _id = data.get("id") or data.get("_id")
        return cls(
            id=str(_id),
            text=str(data.get("text")),
            author=data.get("author"),
            post_id=data.get("post_id", ""),
            parent_id=data.get("parent_id"),
            dislikes=len(data.get("dislikes", [])),
            likes=len(data.get("likes", [])),
            answers_count=data.get("answers_count", 0),
            created_at=data.get("created_at"),  # type: ignore
        )
