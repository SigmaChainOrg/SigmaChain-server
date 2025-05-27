import uuid
from datetime import timedelta
from typing import Optional

from sqlalchemy import UUID, ForeignKey, Integer, Interval, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.configuration import Base
from src.database.models.access_control.group import Group
from src.database.models.access_control.user import User
from src.database.models.workflow.enums import AssigneeEnum, AssigneeEnumSQLA
from src.database.models.workflow.form_pattern import FormPattern


class Activity(Base):
    __tablename__ = "activity"
    __table_args__ = {"schema": "workflow"}

    activity_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
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
    estimated_time: Mapped[timedelta] = mapped_column(
        Interval,
        default=timedelta(seconds=0),
        nullable=False,
    )
    form_pattern_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("workflow.form_pattern.form_pattern_id"),
        default=None,
        nullable=True,
    )
    next_activity_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("workflow.activity.activity_id"),
        default=None,
        nullable=True,
    )

    assignee: Mapped["ActivityAssignees"] = relationship(
        "ActivityAssignees",
        back_populates="activity",
        uselist=False,
        init=False,
    )
    form_pattern: Mapped[FormPattern] = relationship(
        "FormPattern",
        back_populates="activity",
        uselist=False,
        init=False,
    )


class ActivityAssignees(Base):
    __tablename__ = "activity_assignees"
    __table_args__ = {"schema": "workflow"}

    activity_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("workflow.activity.activity_id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )
    assignee_type: Mapped[AssigneeEnum] = mapped_column(
        AssigneeEnumSQLA,
        nullable=False,
    )
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("access_control.user.user_id"),
        nullable=True,
    )
    group_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("access_control.group.group_id"),
        nullable=True,
    )

    user: Mapped[User] = relationship(
        "User",
        uselist=False,
        init=False,
    )
    group: Mapped[Group] = relationship(
        "Group",
        uselist=False,
        init=False,
    )
    activity: Mapped[Activity] = relationship(
        "Activity",
        back_populates="assignee",
        uselist=False,
        init=False,
    )


class ActivityFieldDisplay(Base):
    __tablename__ = "activity_field_display"
    __table_args__ = {"schema": "workflow"}

    activity_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        nullable=False,
    )
    form_field_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        nullable=False,
    )
