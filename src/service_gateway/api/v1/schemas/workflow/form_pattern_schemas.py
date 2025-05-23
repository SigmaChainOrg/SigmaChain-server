from typing import List, Optional

from pydantic import BaseModel, ConfigDict

from src.service_gateway.api.v1.schemas.workflow.form_field_schemas import (
    FormFieldInput,
    FormFieldRead,
    FormFieldUpdate,
)


class FormPatternRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    form_pattern_id: int
    created_at: str
    updated_at: str
    fields: List[FormFieldRead]


class FormPatternInput(BaseModel):
    fields: List[FormFieldInput]


class FormPatternUpdate(BaseModel):
    fields: Optional[List[FormFieldUpdate]] = None
    fields_to_delete: Optional[List[int]] = []
