from enum import StrEnum


class IdTypeEnum(StrEnum):
    ID_CARD = "id_card"
    PASSPORT = "passport"


class RoleEnum(StrEnum):
    REQUESTER = "requester"
    REVIEWER = "reviewer"
    SUPERVISOR = "supervisor"
    MANAGER = "manager"


class ResourceEnum(StrEnum):
    OWN_REQUESTS = "own_requests"
    ALL_REQUESTS = "all_requests"
    OWN_PATTERNS = "own_patterns"
    ALL_PATTERNS = "all_patterns"


class OperationEnum(StrEnum):
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
