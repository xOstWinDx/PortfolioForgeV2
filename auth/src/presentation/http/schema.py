from pydantic import BaseModel


class CredentialsSchema(BaseModel):
    access_token: str
    refresh_token: str
