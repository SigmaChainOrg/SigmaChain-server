from datetime import date, datetime
from typing import Annotated, Optional
from uuid import UUID

from pydantic import (
    BaseModel,
    EmailStr,
    Field,
    SecretStr,
    constr,
    field_serializer,
)

from src.database.models.access_control.enums import IdTypeEnum


class UserSignUpSchema(BaseModel):
    email: EmailStr
    password: SecretStr = Field(exclude=True, repr=False)
    confirm_password: SecretStr = Field(exclude=True, repr=False)


class UserInfoSchema(BaseModel):
    user_info_id: Optional[UUID]
    first_name: Annotated[str, constr(min_length=2, max_length=255)]
    last_name: Annotated[str, constr(min_length=2, max_length=255)]
    id_type: IdTypeEnum
    id_number: Annotated[str, constr(min_length=2, max_length=50)]
    birth_date: date

    @field_serializer("user_info_id")
    def serialize_uuid(self, user_info_id: UUID, _info):
        return str(user_info_id)

    class Config:
        from_attributes = True


class UserSchema(BaseModel):
    user_id: UUID
    email: EmailStr
    is_active: bool
    is_verified: bool
    created_at: datetime
    user_info: Optional[UserInfoSchema]

    @field_serializer("user_id")
    def serialize_uuid(self, user_id: UUID, _info):
        return str(user_id)

    @field_serializer("created_at")
    def serialize_datetime(self, dt: datetime, _info):
        return dt.isoformat()

    class Config:
        from_attributes = True


class UserInDBSchema(UserSchema):
    hashed_password: str
