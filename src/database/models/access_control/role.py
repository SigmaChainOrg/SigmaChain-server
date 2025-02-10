from sqlalchemy import UUID, Column, Enum, ForeignKey
from sqlalchemy.orm import relationship

from src.database.configuration import Base
from src.database.models.access_control.enums import (
    OperationEnum,
    ResourceEnum,
    RoleEnum,
)


class UserRoles(Base):
    __tablename__ = "user_roles"
    __table_args__ = {"schema": "access_control"}

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("access_control.user.user_id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )
    role = Column(
        Enum(RoleEnum, name="role_enum", schema="access_control"),
        primary_key=True,
        nullable=False,
    )

    user = relationship("User", back_populates="roles", uselist=False)


class Policy(Base):
    __tablename__ = "policy"
    __table_args__ = {"schema": "access_control"}

    policy_id = Column(UUID(as_uuid=True), primary_key=True, nullable=False)
    role = Column(
        Enum(RoleEnum, name="role_enum", schema="access_control"), nullable=False
    )
    resource = Column(
        Enum(ResourceEnum, name="resource_enum", schema="access_control"),
        nullable=False,
    )
    operation = Column(
        Enum(OperationEnum, name="operation_enum", schema="access_control"),
        nullable=False,
    )
