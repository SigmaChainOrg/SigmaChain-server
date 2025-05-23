from typing import List, Optional

from pydantic import BaseModel, ConfigDict, field_validator

from src.database.models.workflow.enums import InputTypeEnum
from src.service_gateway.api.v1.schemas.workflow.field_option_schemas import (
    FieldOptionInput,
    FieldOptionRead,
)


class FormFieldRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    form_field_id: int
    form_field_order: int
    input_type: InputTypeEnum
    title: str
    description: Optional[str]
    is_mandatory: Optional[bool] = False
    options: Optional[List[FieldOptionRead]] = None


class FormFieldInput(BaseModel):
    form_field_order: int
    input_type: InputTypeEnum
    title: str
    description: Optional[str] = None
    is_mandatory: Optional[bool] = False
    options: Optional[List[FieldOptionInput]] = None

    @field_validator("options")
    def validate_options(cls, v, values):
        input_type = values.get("input_type")
        if input_type in (InputTypeEnum.SINGLE_CHOICE, InputTypeEnum.MULTIPLE_CHOICE):
            if not v or len(v) == 0:
                raise ValueError("At least one option is required for choice fields.")
            if input_type == InputTypeEnum.SINGLE_CHOICE and len(v) < 2:
                raise ValueError("Single choice fields require at least two options.")
        return v


class FormFieldUpdate(BaseModel):
    form_field_id: Optional[int] = None
    form_field_order: Optional[int] = None
    input_type: Optional[InputTypeEnum] = None
    title: Optional[str] = None
    description: Optional[str] = None
    is_mandatory: Optional[bool] = None
    options: Optional[List[FieldOptionInput]] = None

    @field_validator("options")
    def validate_options_update(cls, v, values):
        input_type = values.get("input_type")
        if input_type is None:
            return v
        if input_type in (InputTypeEnum.SINGLE_CHOICE, InputTypeEnum.MULTIPLE_CHOICE):
            if not v or len(v) == 0:
                raise ValueError("At least one option is required for choice fields.")
            if input_type == InputTypeEnum.SINGLE_CHOICE and len(v) < 2:
                raise ValueError("Single choice fields require at least two options.")
        return v
