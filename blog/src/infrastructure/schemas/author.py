from pydantic import BaseModel


class AuthorSchema(BaseModel):
    id: str
    name: str
    email: str
    photo_url: str
