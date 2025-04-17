from pydantic import BaseModel


class ExceptionSchema(BaseModel):
    code: str
    message: str
    details: str | None = None
