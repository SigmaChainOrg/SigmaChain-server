from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, field_serializer, model_validator

from src.database.models.workflow.enums import AssigneeEnum
from src.utils.serializers import serialize_uuid


class ActivityAsigneesRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    assignee_type: AssigneeEnum
    user_id: Optional[UUID] = None
    group_id: Optional[UUID] = None

    @field_serializer("user_id")
    def serialize_user_id(self, value: UUID):
        return serialize_uuid(value)

    @field_serializer("group_id")
    def serialize_group_id(self, value: UUID):
        return serialize_uuid(value)


class ActivityAsigneesInput(BaseModel):
    assignee_type: AssigneeEnum
    user_id: Optional[UUID] = None
    group_id: Optional[UUID] = None

    @model_validator(mode="after")
    def check_assignments(self) -> "ActivityAsigneesInput":
        if self.assignee_type == AssigneeEnum.REQUESTER:
            if self.user_id is not None or self.group_id is not None:
                raise ValueError(
                    "If assignee_type is 'requester', both user_id and group_id must be None."
                )
        elif self.assignee_type == AssigneeEnum.USER:
            if self.user_id is None:
                raise ValueError("If assignee_type is 'user', user_id is required.")
            if self.group_id is not None:
                raise ValueError("If assignee_type is 'user', group_id must be None.")
        elif self.assignee_type == AssigneeEnum.GROUP:
            if self.group_id is None:
                raise ValueError("If assignee_type is 'group', group_id is required.")
            if self.user_id is not None:
                raise ValueError("If assignee_type is 'group', user_id must be None.")
        return self
