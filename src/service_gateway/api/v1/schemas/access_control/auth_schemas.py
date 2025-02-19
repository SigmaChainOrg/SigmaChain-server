from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, field_serializer


class TokenSchema(BaseModel):
    access_token: str
    token_type: str


class SecureCodeSchema(BaseModel):
    secure_code_id: UUID
    expires_at: datetime

    @field_serializer("secure_code_id")
    def serialize_uuid(self, secure_code_id: UUID, _info):
        return str(secure_code_id)

    @field_serializer("expires_at")
    def serialize_datetime(self, dt: datetime, _info):
        return dt.isoformat()

    class Config:
        from_attributes = True


class SecureCodeInput(BaseModel):
    secure_code_id: UUID
    code: str
