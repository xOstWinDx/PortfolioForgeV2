from pydantic import BaseModel

class ValidationErrorSchema(BaseModel):
    loc: list[str | int]  # Местоположение ошибки
    msg: str  # Сообщение об ошибке
    type: str  # Тип ошибки
    ctx: dict[str, Any] | None = None  # Дополнительный контекст (если имеется)


class ExceptionSchema(BaseModel):
    code: str
    message: str
    details: str | None = None