from datetime import timedelta
from typing import Optional

from pydantic import BaseModel, ConfigDict, field_serializer

from src.service_gateway.api.v1.schemas.workflow.activity_asignees_schemas import (
    ActivityAsigneesInput,
    ActivityAsigneesRead,
    ActivityAsigneesUpdate,
)
from src.utils.serializers import serialize_timedelta


class ActivityRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    activity_order: int
    activity_id: int
    label: str
    description: str
    assignee: Optional[ActivityAsigneesRead] = None
    form_id: Optional[int] = None
    next_activity_id: Optional[int] = None
    estimated_time: Optional[timedelta] = None

    @field_serializer("estimated_time")
    def serialize_estimated_time(self, value: timedelta) -> float:
        return serialize_timedelta(value)


class ActivityInput(BaseModel):
    activity_order: int
    label: str
    description: str
    assignee: Optional[ActivityAsigneesInput] = None


class ActivityUpdate(BaseModel):
    label: Optional[str] = None
    description: Optional[str] = None
    assignee: Optional[ActivityAsigneesUpdate] = None
    form_id: Optional[int] = None
    next_activity_id: Optional[int] = None
    estimated_time: Optional[timedelta] = None
