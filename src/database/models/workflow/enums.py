from enum import StrEnum

from sqlalchemy import Enum


class AssigneeEnum(StrEnum):
    USER = "user"
    GROUP = "group"
    REQUESTER = "requester"


AssigneeEnumSQLA = Enum(
    AssigneeEnum,
    name="assignee_enum",
    schema="workflow",
    values_callable=lambda x: [e.value for e in x],
)


class InputTypeEnum(StrEnum):
    SECTION = "section"
    SHORT_TEXT = "short_text"
    LONG_TEXT = "long_text"
    SINGLE_CHOICE = "single_choice"
    MULTIPLE_CHOICE = "multiple_choice"
    FILE_UPLOAD = "file_upload"


InputTypeEnumSQLA = Enum(
    InputTypeEnum,
    name="input_type_enum",
    schema="workflow",
    values_callable=lambda x: [e.value for e in x],
)
