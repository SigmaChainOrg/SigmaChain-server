from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import UUID, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.configuration import Base
from src.database.models.access_control.enums import (
    OperationEnum,
    OperationEnumSQLA,
    ResourceEnum,
    ResourceEnumSQLA,
    RoleEnum,
    RoleEnumSQLA,
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
        RoleEnumSQLA,
        primary_key=True,
        nullable=False,
    )

    user: Mapped["User"] = relationship(
        "User",
        back_populates="roles",
        uselist=False,
        init=False,
    )


class Policy(Base):
    __tablename__ = "policy"
    __table_args__ = {"schema": "access_control"}

    policy_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
        init=False,
    )
    role: Mapped[RoleEnum] = mapped_column(RoleEnumSQLA, nullable=False)
    resource: Mapped[ResourceEnum] = mapped_column(ResourceEnumSQLA, nullable=False)
    operation: Mapped[OperationEnum] = mapped_column(OperationEnumSQLA, nullable=False)
