from datetime import date, datetime
from typing import Annotated, Optional
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    SecretStr,
    constr,
    field_serializer,
)

from src.database.models.access_control.enums import IdTypeEnum


class UserSignUpInput(BaseModel):
    email: EmailStr
    password: SecretStr = Field(exclude=True, repr=False)
    confirm_password: SecretStr = Field(exclude=True, repr=False)


class UserInfoSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    first_name: Annotated[str, constr(min_length=2, max_length=255)]
    last_name: Annotated[str, constr(min_length=2, max_length=255)]
    id_type: IdTypeEnum
    id_number: Annotated[str, constr(min_length=2, max_length=50)]
    birth_date: date

    @field_serializer("birth_date")
    def serialize_date(self, dt: date, _info):
        return dt.isoformat()


class UserInfoUpdate(BaseModel):
    first_name: Optional[Annotated[str, constr(min_length=2, max_length=255)]] = None
    last_name: Optional[Annotated[str, constr(min_length=2, max_length=255)]] = None
    id_type: Optional[IdTypeEnum] = None
    id_number: Optional[Annotated[str, constr(min_length=2, max_length=50)]] = None
    birth_date: Optional[date] = None


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
