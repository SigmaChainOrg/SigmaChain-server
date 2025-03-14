from enum import StrEnum

from sqlalchemy import Enum


class IdTypeEnum(StrEnum):
    ID_CARD = "id_card"
    PASSPORT = "passport"


IdTypeEnumSQLA = Enum(
    IdTypeEnum,
    name="id_type_enum",
    schema="access_control",
    values_callable=lambda x: [e.value for e in x],
)


class RoleEnum(StrEnum):
    REQUESTER = "requester"
    REVIEWER = "reviewer"
    SUPERVISOR = "supervisor"
    MANAGER = "manager"


RoleEnumSQLA = Enum(
    RoleEnum,
    name="role_enum",
    schema="access_control",
    values_callable=lambda x: [e.value for e in x],
)


class ResourceEnum(StrEnum):
    OWN_REQUESTS = "own_requests"
    ALL_REQUESTS = "all_requests"
    OWN_PATTERNS = "own_patterns"
    ALL_PATTERNS = "all_patterns"


ResourceEnumSQLA = Enum(
    ResourceEnum,
    name="resource_enum",
    schema="access_control",
    values_callable=lambda x: [e.value for e in x],
)


class OperationEnum(StrEnum):
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"


OperationEnumSQLA = Enum(
    OperationEnum,
    name="operation_enum",
    schema="access_control",
    values_callable=lambda x: [e.value for e in x],
)
