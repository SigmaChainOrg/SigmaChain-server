from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Dict

from sqlalchemy import UUID, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.configuration import Base

if TYPE_CHECKING:
    from src.database.models.access_control.user import User


@dataclass
class UserGroups(Base):
    __tablename__ = "user_groups"
    __table_args__ = {"schema": "access_control"}

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("access_control.user.user_id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )
    group_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("access_control.group.group_id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )

    user: Mapped["User"] = relationship(
        "User",
        back_populates="groups",
        uselist=False,
        lazy="joined",
    )
    group: Mapped["Group"] = relationship(
        "Group",
        back_populates="users",
        uselist=False,
        lazy="joined",
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "user_id": self.user_id,
            "group_id": self.group_id,
        }


@dataclass
class Group(Base):
    __tablename__ = "group"
    __table_args__ = {"schema": "access_control"}

    group_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
        init=False,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    parent_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("access_control.group.group_id"),
        nullable=True,
    )

    users: Mapped[list["UserGroups"]] = relationship(
        "UserGroups", back_populates="group", init=False
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "group_id": self.group_id,
            "name": self.name,
            "parent_id": self.parent_id,
        }
