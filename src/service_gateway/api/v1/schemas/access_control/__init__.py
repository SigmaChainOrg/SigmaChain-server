from src.service_gateway.api.v1.schemas.access_control.group_schemas import (
    GroupSimpleRead,
)
from src.service_gateway.api.v1.schemas.access_control.user_schemas import UserRead

UserRead.model_rebuild()
GroupSimpleRead.model_rebuild()
