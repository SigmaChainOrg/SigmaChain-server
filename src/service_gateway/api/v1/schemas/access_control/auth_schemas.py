from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, field_serializer

from src.utils.serializers import serialize_datetime


class TokenRead(BaseModel):
    access_token: str
    token_type: str


class SecureCodeRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    secure_code_id: UUID
    expires_at: datetime

    @field_serializer("secure_code_id")
    def serialize_uuid(self, secure_code_id: UUID, _info):
        return str(secure_code_id)

    @field_serializer("expires_at")
    def serialize_expires_at(self, dt: datetime, _info):
        return serialize_datetime(dt)


class SecureCodeValidate(BaseModel):
    secure_code_id: UUID
    code: str
