# Load all the models in the database package to ensure they are registered in SQLAlchemy.
from src.database.models.access_control.group import (  # type: ignore # noqa
    Group,
    UserGroups,
)
from src.database.models.access_control.role import (  # type: ignore # noqa
    Policy,
    UserRoles,
)
from src.database.models.access_control.secure_code import SecureCode  # type: ignore # noqa
from src.database.models.access_control.user import (  # type: ignore # noqa
    User,
    UserInfo,
)
from src.database.models.workflow.activity import (  # type: ignore # noqa
    Activity,
    ActivityAssignees,
)
from src.database.models.workflow.field_option import FieldOption  # type: ignore # noqa
from src.database.models.workflow.form_field import FormField  # type: ignore # noqa
from src.database.models.workflow.form_pattern import FormPattern  # type: ignore # noqa
from src.database.models.workflow.request_pattern import (  # type: ignore # noqa
    RequestGroups,
    RequestPattern,
)
