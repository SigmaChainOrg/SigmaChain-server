# Load all the models in the database package to ensure they are registered in SQLAlchemy.
from src.database.models.access_control.user import User, UserInfo  # type: ignore # noqa
from src.database.models.access_control.group import Group, UserGroups  # type: ignore # noqa
from src.database.models.access_control.role import UserRoles, Policy  # type: ignore # noqa
