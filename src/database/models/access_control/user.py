from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, List

from sqlalchemy import UUID, Boolean, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from src.database.configuration import Base
from src.database.models.access_control.enums import IdTypeEnum, IdTypeEnumSQLA

if TYPE_CHECKING:
    from src.database.models.access_control.group import Group
    from src.database.models.access_control.role import UserRoles


class User(Base):
    __tablename__ = "user"
    __table_args__ = {"schema": "access_control"}

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        init=False,
    )
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False,
        init=False,
    )

    user_info: Mapped["UserInfo"] = relationship(
        "UserInfo",
        back_populates="user",
        uselist=False,
        lazy="joined",
        init=False,
    )
    roles: Mapped[List["UserRoles"]] = relationship(
        "UserRoles",
        back_populates="user",
        init=False,
    )
    groups: Mapped[List["Group"]] = relationship(
        "Group",
        secondary="access_control.user_groups",
        back_populates="users",
        overlaps="group",
        init=False,
    )

    def to_dict(self, with_user_info: bool = False) -> Dict[str, Any]:
        user_dict = {
            "user_id": self.user_id,
            "email": self.email,
            "is_active": self.is_active,
            "is_verified": self.is_verified,
            "created_at": self.created_at,
        }

        if with_user_info:
            user_dict["user_info"] = self.user_info.to_dict()

        return user_dict


class UserInfo(Base):
    __tablename__ = "user_info"
    __table_args__ = {"schema": "access_control"}

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("access_control.user.user_id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
        unique=True,
    )
    first_name: Mapped[str] = mapped_column(String(255), nullable=False)
    last_name: Mapped[str] = mapped_column(String(255), nullable=False)
    id_type: Mapped[IdTypeEnum] = mapped_column(IdTypeEnumSQLA, nullable=False)
    id_number: Mapped[str] = mapped_column(String(50), nullable=False)
    birth_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        init=False,
    )

    user: Mapped["User"] = relationship(
        User,
        back_populates="user_info",
        uselist=False,
        lazy="joined",
        init=False,
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "user_id": self.user_id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "id_type": self.id_type.value,
            "id_number": self.id_number,
            "birth_date": self.birth_date,
        }
