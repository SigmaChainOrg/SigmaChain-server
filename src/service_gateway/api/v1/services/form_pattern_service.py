from collections import Counter
from typing import Dict, List, Literal, Optional

from sqlalchemy import literal_column
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from src.database.models.workflow.enums import InputTypeEnum
from src.database.models.workflow.field_option import FieldOption
from src.database.models.workflow.form_field import FormField
from src.database.models.workflow.form_pattern import FormPattern
from src.service_gateway.api.v1.schemas.workflow.form_field_schemas import (
    FormFieldInput,
    FormFieldRead,
)
from src.service_gateway.api.v1.schemas.workflow.form_pattern_schemas import (
    FormPatternInput,
    FormPatternRead,
    FormPatternUpdate,
)
from src.utils.http_exceptions import BadRequestError


class FieldsChain:
    """Class to represent a chain of form fields"""

    def __init__(self) -> None:
        self.form_fields: Dict[int, FormField] = {}

    ## Friendly methods

    def _add_field(self, form_field: FormField) -> None:
        count = len(self.form_fields)
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

    def _get_field_by_id(self, field_id: int) -> Optional[FormField]:
        for field in self.form_fields.values():
            if field.form_field_id == field_id:
                return field
        return None

    def _get_field_ids_to_update_or_delete(
        self, fields_to_update: List[int]
    ) -> Dict[Literal["update", "delete"], List[int]]:
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

    async def _get_form_pattern_by_id(
        self, form_pattern_id: int
    ) -> Optional[FormPattern]:
        stmt = select(FormPattern).where(FormPattern.form_pattern_id == form_pattern_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

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

    async def _create_form_field(self, field_input: FormFieldInput) -> FormField:
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

        return new_form_field

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

            if i == 0 and field_input.input_type != InputTypeEnum.SECTION:
                raise BadRequestError("The first field must be a section field.")

            if i == 1 and field_input.input_type == InputTypeEnum.SECTION:
                raise BadRequestError("The second field must not be a section field.")

            new_form_field = await self._create_form_field(field_input)

            if last_field:
                last_field.next_field_id = new_form_field.form_field_id

            if i == 0:
                first_field_id = new_form_field.form_field_id

            last_field = new_form_field

            await self.db.flush()
            await self.db.refresh(new_form_field)

        form_pattern = FormPattern(form_field_id=first_field_id)

        return form_pattern

    ## Public methods

    async def get_form_pattern(self, form_pattern_id: int) -> FormPatternRead:
        form_pattern = await self._get_form_pattern_by_id(form_pattern_id)

        if not form_pattern:
            raise BadRequestError(f"Form pattern with ID {form_pattern_id} not found.")

        fields_chain = await self._get_form_fields_chain(form_pattern.form_field_id)
        fields_read = fields_chain._to_fields_read()

        return FormPatternRead.model_validate(
            {**form_pattern.to_dict(), "fields": fields_read}
        )

    async def update_form_pattern(
        self, form_pattern_id: int, update: FormPatternUpdate
    ) -> FormPatternRead:
        try:
            form_pattern = await self._get_form_pattern_by_id(form_pattern_id)

            if not form_pattern:
                raise BadRequestError(
                    f"Form pattern with ID {form_pattern_id} not found."
                )

            if form_pattern.is_published:
                raise BadRequestError("Cannot update a published form pattern.")

            fields_update = sorted(update.fields, key=lambda x: x.form_field_order)

            if len(fields_update) != len(
                set(field.form_field_order for field in fields_update)
            ):
                raise BadRequestError("Form pattern fields must have unique orders.")

            if len(fields_update) < 2:
                raise BadRequestError(
                    "Form pattern must have at least 2 fields (one section and one field)."
                )

            # 1. Get the actual fields chain
            actual_fields_chain = await self._get_form_fields_chain(
                form_pattern.form_field_id
            )

            # 2. Validate the fields to update
            ids_to_update = [
                field.form_field_id for field in update.fields if field.form_field_id
            ]

            fields_update_or_delete = (
                actual_fields_chain._get_field_ids_to_update_or_delete(
                    fields_to_update=ids_to_update
                )
            )

            if Counter(ids_to_update) != Counter(
                fields_update_or_delete.get("update", [])
            ):
                raise BadRequestError(
                    "Fields to update do not match the existing fields in the form pattern."
                )
            if Counter(update.fields_to_delete) != Counter(
                fields_update_or_delete.get("delete", [])
            ):
                raise BadRequestError(
                    "Fields to delete do not match the existing fields in the form pattern."
                )

            # 3. Delete fields that are marked for deletion
            for field_id in update.fields_to_delete:
                field_to_delete = actual_fields_chain._get_field_by_id(field_id)
                if not field_to_delete:
                    raise BadRequestError(f"Field with ID {field_id} not found.")

                await self.db.delete(field_to_delete)

            await self.db.flush()

            # 4. Create new field chain, with updated fields and new fields
            first_field_id: int = 0
            last_field: Optional[FormField] = None

            for i, field_update_data in enumerate(fields_update):
                if i != field_update_data.form_field_order:
                    raise BadRequestError(
                        f"Form pattern fields must have continuous orders starting from 0."
                        f"Expected order {i}, but got {field_update_data.form_field_order}."
                    )

                if i == 0 and (
                    field_update_data.input_type is not None
                    and field_update_data.input_type != InputTypeEnum.SECTION
                ):
                    raise BadRequestError("The first field must be a section field.")

                if i == 1 and (
                    field_update_data.input_type is not None
                    and field_update_data.input_type == InputTypeEnum.SECTION
                ):
                    raise BadRequestError(
                        "The second field must not be a section field."
                    )

                if field_update_data.form_field_id:
                    # A. Update existing field
                    field_to_update = actual_fields_chain._get_field_by_id(
                        field_update_data.form_field_id
                    )

                    if not field_to_update:
                        raise BadRequestError(
                            f"Field with ID {field_update_data.form_field_id} not found."
                        )

                    if field_update_data.title is not None:
                        field_to_update.title = field_update_data.title

                    if field_update_data.description is not None:
                        field_to_update.description = field_update_data.description

                    if field_update_data.is_mandatory is not None:
                        field_to_update.is_mandatory = field_update_data.is_mandatory

                    if field_update_data.input_type is not None:
                        if field_to_update.input_type in [
                            InputTypeEnum.SINGLE_CHOICE,
                            InputTypeEnum.MULTIPLE_CHOICE,
                        ] and field_update_data not in [
                            InputTypeEnum.SINGLE_CHOICE,
                            InputTypeEnum.MULTIPLE_CHOICE,
                        ]:
                            for option in field_to_update.options:
                                await self.db.delete(option)

                        field_to_update.input_type = field_update_data.input_type

                    if (
                        field_update_data.options is not None
                        and field_to_update.input_type
                        in [
                            InputTypeEnum.SINGLE_CHOICE,
                            InputTypeEnum.MULTIPLE_CHOICE,
                        ]
                    ):
                        for option in field_to_update.options:
                            await self.db.delete(option)

                        for i, option_input in enumerate(field_to_update.options):
                            if i != option_input.option_order:
                                raise BadRequestError(
                                    f"Form field options must have continuous orders starting from 0."
                                    f"Expected order {i}, but got {option_input.option_order}."
                                )

                            field_option = FieldOption(
                                form_field_id=field_to_update.form_field_id,
                                title=option_input.title,
                                option_order=option_input.option_order,
                            )
                            self.db.add(field_option)

                        field_to_update.next_field_id = None
                        field_to_order = field_to_update

                else:
                    # B. Create new field
                    field_to_order = await self._create_form_field(
                        FormFieldInput.model_validate(field_update_data)
                    )

                if last_field:
                    last_field.next_field_id = field_to_order.form_field_id

                if i == 0:
                    first_field_id = field_to_order.form_field_id

                last_field = field_to_order

                await self.db.flush()
                await self.db.refresh(field_to_order)

            form_pattern.form_field_id = first_field_id

            await self.db.refresh(form_pattern)

            fields_chain = await self._get_form_fields_chain(form_pattern.form_field_id)
            fields_read = fields_chain._to_fields_read()

            form_pattern_read = FormPatternRead.model_validate(
                {**form_pattern.to_dict(), "fields": fields_read}
            )

            await self.db.commit()
            return form_pattern_read

            # Create new
        except Exception:
            await self.db.rollback()
            raise
