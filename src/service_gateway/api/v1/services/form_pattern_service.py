from typing import Dict, List, Literal, Optional
from uuid import UUID

from sqlalchemy import literal_column
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from src.database.models.workflow.enums import InputTypeEnum
from src.database.models.workflow.field_option import FieldOption
from src.database.models.workflow.form_field import FormField
from src.database.models.workflow.form_pattern import FormPattern
from src.service_gateway.api.v1.schemas.workflow.form_field_schemas import FormFieldRead
from src.service_gateway.api.v1.schemas.workflow.form_pattern_schemas import (
    FormPatternInput,
)
from src.utils.http_exceptions import BadRequestError


class FieldsChain:
    """Class to represent a chain of form fields"""

    def __init__(self) -> None:
        self.form_fields: Dict[int, FormField] = {}

    ## Friendly methods

    def _add_field(self, form_field: FormField) -> None:
        count = len(self.form_fields) + 1
        self.form_fields[count] = form_field

    def _to_fields_read(self) -> List[FormFieldRead]:
        return [
            FormFieldRead.model_validate(
                dict(
                    **field.to_dict(),
                    form_field_order=key,
                )
            )
            for key, field in self.form_fields.items()
        ]

    def _get_field_by_order(self, order: int) -> Optional[FormField]:
        return self.form_fields.get(order)

    def _get_field_by_id(self, field_id: UUID) -> Optional[FormField]:
        for field in self.form_fields.values():
            if field.form_field_id == field_id:
                return field
        return None

    def _get_field_ids_to_update_or_delete(
        self, fields_to_update: List[UUID]
    ) -> Dict[Literal["update", "delete"], List[UUID]]:
        fields_on_chain_to_update = []
        fields_on_chain_to_delete = []

        for field in self.form_fields.values():
            if field.form_field_id in fields_to_update:
                fields_on_chain_to_update.append(field.form_field_id)
            else:
                fields_on_chain_to_delete.append(field.form_field_id)

        return {
            "update": fields_on_chain_to_update,
            "delete": fields_on_chain_to_delete,
        }


class FormPatternService:
    def __init__(self, db: AsyncSession):
        self.db = db

    ## Friendly methods

    async def _get_form_fields_chain(
        self,
        first_field_id: int,
    ) -> FieldsChain:
        form_fields_cte = (
            select(FormField)
            .add_columns(literal_column("0").label("order"))
            .where(FormField.form_field_id == first_field_id)
            .cte(name="form_fields_chain", recursive=True)
        )

        cte_alias = form_fields_cte.alias("form_fields_chain_alias")

        form_fields_cte = form_fields_cte.union_all(
            select(FormField)
            .add_columns((cte_alias.c.order + 1).label("order"))
            .join(cte_alias, FormField.form_field_id == cte_alias.c.next_field_id)
        )

        stmt = (
            select(FormField, form_fields_cte.c.order)
            .join(
                form_fields_cte,
                FormField.form_field_id == form_fields_cte.c.form_field_id,
            )
            .order_by(form_fields_cte.c.order)
        ).options(selectinload(FormField.options))

        result = await self.db.execute(stmt)

        fields_chain = FieldsChain()

        for form_field, order in result.all():
            fields_chain._add_field(form_field)

        return fields_chain

    async def _create_form_pattern_without_commit(
        self, input: FormPatternInput
    ) -> FormPattern:
        fields_input = sorted(input.fields, key=lambda x: x.form_field_order)

        first_field_id: int = 0
        last_field: Optional[FormField] = None

        if len(fields_input) < 2:
            raise BadRequestError(
                "Form pattern must have at least 2 fields (one section and one field)."
            )

        if len(fields_input) != len(
            set(field.form_field_order for field in fields_input)
        ):
            raise BadRequestError("Form pattern fields must have unique orders.")

        for i, field_input in enumerate(fields_input):
            if i != field_input.form_field_order:
                raise BadRequestError(
                    f"Form pattern fields must have continuous orders starting from 0."
                    f"Expected order {i}, but got {field_input.form_field_order}."
                )

            new_form_field = FormField(
                input_type=field_input.input_type,
                title=field_input.title,
                description=field_input.description,
                is_mandatory=field_input.is_mandatory,
            )

            self.db.add(new_form_field)
            await self.db.flush()
            await self.db.refresh(new_form_field)

            options = (
                sorted(field_input.options, key=lambda x: x.option_order)
                if field_input.options
                else []
            )

            if len(options) != len(set(option.option_order for option in options)):
                raise BadRequestError("Form field options must have unique orders.")

            if new_form_field.input_type in [
                InputTypeEnum.SINGLE_CHOICE,
                InputTypeEnum.MULTIPLE_CHOICE,
            ]:
                for i, option_input in enumerate(options):
                    if i != option_input.option_order:
                        raise BadRequestError(
                            f"Form field options must have continuous orders starting from 0."
                            f"Expected order {i}, but got {option_input.option_order}."
                        )

                    field_option = FieldOption(
                        form_field_id=new_form_field.form_field_id,
                        title=option_input.title,
                        option_order=option_input.option_order,
                    )
                    self.db.add(field_option)

            if last_field:
                last_field.next_field_id = new_form_field.form_field_id

            if i == 0:
                first_field_id = new_form_field.form_field_id

            last_field = new_form_field

            await self.db.flush()
            await self.db.refresh(new_form_field)

        form_pattern = FormPattern(form_field_id=first_field_id)

        return form_pattern
