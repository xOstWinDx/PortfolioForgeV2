from typing import Any

from pydantic import BaseModel, Field


class AuthenticationErrorSchema(BaseModel):
    detail: str = Field(examples=["Invalid Token", "Incorrect Email or Password"])


class AuthorizationErrorSchema(BaseModel):
    detail: str = Field(examples=["You don't have permission to perform this action"])


class ConflictErrorSchema(BaseModel):
    detail: str = Field(
        examples=["User with email new_user@example.com.ru already exists"]
    )


class NotFoundErrorSchema(BaseModel):
    detail: str = Field(examples=["User not found"])


class ErrorDetail(BaseModel):
    loc: list[str | int]  # Местоположение ошибки
    msg: str  # Сообщение об ошибке
    type: str  # Тип ошибки
    ctx: dict[str, Any] | None = None  # Дополнительный контекст (если имеется)
