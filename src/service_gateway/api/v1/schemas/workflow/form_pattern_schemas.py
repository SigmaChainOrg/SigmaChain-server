from datetime import datetime
from typing import List

from pydantic import BaseModel, ConfigDict, field_serializer

from src.service_gateway.api.v1.schemas.workflow.form_field_schemas import (
    FormFieldInput,
    FormFieldRead,
    FormFieldUpdate,
)
from src.utils.serializers import serialize_datetime


class FormPatternRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    form_pattern_id: int
    created_at: datetime
    updated_at: datetime
    fields: List[FormFieldRead]

    @field_serializer("created_at", "updated_at")
    def serialize_datetime(self, value: datetime):
        return serialize_datetime(value)


class FormPatternInput(BaseModel):
    fields: List[FormFieldInput]


class FormPatternUpdate(BaseModel):
    fields: List[FormFieldUpdate] = []
    fields_to_delete: List[int] = []
