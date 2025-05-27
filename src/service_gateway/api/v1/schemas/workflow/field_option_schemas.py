from pydantic import BaseModel, ConfigDict


class FieldOptionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    field_option_id: int
    form_field_id: int
    title: str
    option_order: int


class FieldOptionInput(BaseModel):
    title: str
    option_order: int
