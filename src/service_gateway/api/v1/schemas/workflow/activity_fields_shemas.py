from pydantic import BaseModel, ConfigDict

from src.database.models.workflow.enums import InputTypeEnum


class FieldDisplayRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    form_field_id: int
    form_field_order: int
    title: str
    input_type: InputTypeEnum
    selected: bool


class ActivityFieldsRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    activity_id: int
    activity_order: int
    label: str
    fields: list[FieldDisplayRead]


class ActivityFieldsInput(BaseModel):
    fields: list[int]
