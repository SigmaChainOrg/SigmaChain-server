import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import UUID, Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from src.database.configuration import Base
from src.database.models.access_control.group import Group
from src.database.models.access_control.user import User


class RequestPattern(Base):
    __tablename__ = "request_pattern"
    __table_args__ = {"schema": "workflow"}

    request_pattern_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        init=False,
    )
    label: Mapped[str] = mapped_column(
        String(255),
        index=True,
        nullable=False,
    )
    description: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )
    supervisor_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("access_control.user.user_id"),
        nullable=True,
    )
    activity_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("workflow.activity.activity_id"),
        nullable=True,
    )
    published_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        init=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False,
        init=False,
    )

    supervisor: Mapped[User] = relationship(
        "User",
        uselist=False,
        init=False,
    )
    groups: Mapped[List[Group]] = relationship(
        "Group",
        secondary="workflow.request_groups",
        overlaps="group",
        init=False,
    )

    @property
    def is_published(self) -> bool:
        return self.published_at is not None


class RequestGroups(Base):
    __tablename__ = "request_groups"
    __table_args__ = {"schema": "workflow"}

    request_pattern_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workflow.request_pattern.request_pattern_id"),
        primary_key=True,
    )
    group_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("access_control.group.group_id"),
        primary_key=True,
    )

    request_pattern: Mapped[RequestPattern] = relationship(
        "RequestPattern",
        overlaps="groups",
        uselist=False,
        init=False,
    )
    group: Mapped[Group] = relationship(
        "Group",
        uselist=False,
        init=False,
    )
