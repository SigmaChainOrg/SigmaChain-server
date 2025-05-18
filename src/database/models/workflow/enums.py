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
