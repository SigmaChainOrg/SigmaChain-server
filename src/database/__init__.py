# Load all the models in the database package to ensure they are registered in SQLAlchemy.
from src.database.models.access_control.user import User, UserInfo  # type: ignore # noqa
