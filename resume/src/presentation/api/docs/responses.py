from typing import Any

from pydantic import BaseModel


class ErrorDetail(BaseModel):
    loc: list[str | int]  # Местоположение ошибки
    msg: str  # Сообщение об ошибке
    type: str  # Тип ошибки
    ctx: dict[str, Any] | None = None  # Дополнительный контекст (если имеется)


R_422 = {
    "description": "Ошибка валидации входных данных",
    "content": {"application/json": {"schema": ErrorDetail.model_json_schema()}},
}
