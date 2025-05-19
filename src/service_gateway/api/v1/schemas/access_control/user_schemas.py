from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING, Annotated, Any, List, Optional
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    constr,
    field_serializer,
    model_validator,
)

from src.database.models.access_control.enums import IdTypeEnum, RoleEnum
from src.utils.serializers import serialize_datetime, serialize_uuid

if TYPE_CHECKING:
    from src.service_gateway.api.v1.schemas.access_control.group_schemas import (
        GroupSimpleRead,
    )


class UserInfoRead(BaseModel):
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


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: UUID
    email: EmailStr
    is_active: bool
    is_verified: bool
    created_at: datetime
    user_info: Optional[UserInfoRead] = None
    groups: Optional[List["GroupSimpleRead"]] = None
    roles: Optional[List[RoleEnum]] = None

    @field_serializer("user_id")
    def serialize_user_uuid(self, user_id: UUID, _info):
        return serialize_uuid(user_id)

    @field_serializer("created_at")
    def serialize_created_at(self, dt: datetime, _info):
        return serialize_datetime(dt)

    @model_validator(mode="before")
    @classmethod
    def extract_roles(cls, data: Any):
        if data is None:
            return data

        if not isinstance(data, dict):
            return data

        if "roles" in data and isinstance(data["roles"], list):
            data["roles"] = [item["role"] for item in data["roles"]]

        return data


# Query schemas


class UserQuery(BaseModel):
    include_user_info: bool = False
    include_groups: bool = False
    include_roles: bool = False
    # ToDo: Uncomment when policies were added to the model
    # include_policies: bool = False


class UserFilters(UserQuery):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=10, ge=1, le=100)
    only_active: bool = True
    only_verified: Optional[bool] = None
    name: Optional[str] = None
