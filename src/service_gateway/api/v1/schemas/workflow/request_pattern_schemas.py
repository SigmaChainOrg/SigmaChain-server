from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, field_serializer

from src.service_gateway.api.v1.schemas.access_control.group_schemas import (
    GroupSimpleRead,
)
from src.service_gateway.api.v1.schemas.workflow.activity_schemas import (
    ActivityInput,
    ActivityRead,
    ActivityUpdate,
)
from src.utils.serializers import serialize_datetime, serialize_uuid


class RequestPatternRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    request_pattern_id: UUID
    label: str
    description: str
    supervisor_id: Optional[UUID] = None
    activity_id: int
    is_published: bool
    published_at: Optional[datetime] = None
    is_active: bool
    created_at: datetime
    groups: Optional[List[GroupSimpleRead]] = None
    activities: Optional[List[ActivityRead]] = None

    @field_serializer("request_pattern_id")
    def serialize_id(self, value: UUID):
        return serialize_uuid(value)

    @field_serializer("published_at")
    def serialize_published_at(self, value: datetime):
        return serialize_datetime(value)

    @field_serializer("created_at")
    def serialize_created_at(self, value: datetime):
        return serialize_datetime(value)


class RequestPatternInput(BaseModel):
    label: str
    description: str
    supervisor_id: Optional[UUID] = None
    groups: List[UUID]
    activities: List[ActivityInput]


class RequestPatternUpdate(BaseModel):
    label: Optional[str] = None
    description: Optional[str] = None
    supervisor_id: Optional[UUID] = None
    groups: Optional[List[UUID]] = None
    activities: Optional[List[ActivityUpdate]] = None
    activities_to_delete: List[int] = []


# Query schemas


class RequestPatternQuery(BaseModel):
    include_groups: bool = False
    include_activities: bool = False


class RequestPatternFilters(BaseModel):
    label: Optional[str] = None
    supervisor_id: Optional[UUID] = None
    is_published: Optional[bool] = None
    is_active: Optional[bool] = None
    include_groups: bool = False
    include_activities: bool = False
