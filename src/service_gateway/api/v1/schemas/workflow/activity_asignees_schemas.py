from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, field_serializer

from src.database.models.workflow.enums import AssigneeEnum
from src.utils.serializers import serialize_uuid


class ActivityAsigneesRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    assignee_type: AssigneeEnum
    user_id: Optional[UUID] = None
    group_id: Optional[UUID] = None

    @field_serializer("user_id")
    def serialize_user_id(self, value: UUID) -> str | None:
        return serialize_uuid(value)

    @field_serializer("group_id")
    def serialize_group_id(self, value: UUID) -> str | None:
        return serialize_uuid(value)


class ActivityAsigneesInput(BaseModel):
    assignee_type: AssigneeEnum
    user_id: Optional[UUID] = None
    group_id: Optional[UUID] = None


class ActivityAsigneesUpdate(BaseModel):
    assignee_type: Optional[AssigneeEnum] = None
    user_id: Optional[UUID] = None
    group_id: Optional[UUID] = None
