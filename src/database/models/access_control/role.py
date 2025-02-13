from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, Any, Dict

from sqlalchemy import UUID, Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.configuration import Base
from src.database.models.access_control.enums import (
    OperationEnum,
    ResourceEnum,
    RoleEnum,
)

if TYPE_CHECKING:
    from src.database.models.access_control.user import User


class UserRoles(Base):
    __tablename__ = "user_roles"
    __table_args__ = {"schema": "access_control"}

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("access_control.user.user_id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )
    role: Mapped[RoleEnum] = mapped_column(
        Enum(RoleEnum, name="role_enum", schema="access_control"),
        primary_key=True,
        nullable=False,
    )

    user: Mapped["User"] = relationship("User", back_populates="roles", uselist=False)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "user_id": self.user_id,
            "role": self.role,
        }


class Policy(Base):
    __tablename__ = "policy"
    __table_args__ = {"schema": "access_control"}

    policy_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        nullable=False,
    )
    role: Mapped[RoleEnum] = mapped_column(
        Enum(RoleEnum, name="role_enum", schema="access_control"),
        nullable=False,
    )
    resource: Mapped[ResourceEnum] = mapped_column(
        Enum(ResourceEnum, name="resource_enum", schema="access_control"),
        nullable=False,
    )
    operation: Mapped[OperationEnum] = mapped_column(
        Enum(OperationEnum, name="operation_enum", schema="access_control"),
        nullable=False,
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "policy_id": self.policy_id,
            "role": self.role,
            "resource": self.resource,
            "operation": self.operation,
        }
