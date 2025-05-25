from typing import Dict, List, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models.workflow.field_option import FieldOption
from src.database.models.workflow.form_field import FormField
from src.database.models.workflow.form_pattern import FormPattern
from src.service_gateway.api.v1.schemas.workflow.form_field_schemas import FormFieldRead
from src.service_gateway.api.v1.schemas.workflow.form_pattern_schemas import (
    FormPatternInput,
)


class FieldsChain:
    """Class to represent a chain of form fields"""

    def __init__(self) -> None:
        self.form_fields: Dict[int, FormField] = {}

    def add_field(self, form_field: FormField) -> None:
        count = len(self.form_fields) + 1
        self.form_fields[count] = form_field

    def to_fields_read(self) -> List[FormFieldRead]:
        return [
            FormFieldRead.model_validate(
                dict(
                    **field.__dict__,
                    form_field_order=key,
                )
            )
            for key, field in self.form_fields.items()
        ]

    def get_field_by_order(self, order: int) -> Optional[FormField]:
        return self.form_fields.get(order)

    def get_field_by_id(self, field_id: UUID) -> Optional[FormField]:
        for field in self.form_fields.values():
            if field.form_field_id == field_id:
                return field
        return None


class FormPatternService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def _create_form_pattern_without_commit(
        self, input: FormPatternInput
    ) -> FormPattern:
        form_pattern = FormPattern(**input.model_dump())
        self.db.add(form_pattern)

        return form_pattern

        return form_pattern
