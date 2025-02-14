from pydantic import BaseModel


class TokenSchema(BaseModel):
    access_token: str
    token_type: str
