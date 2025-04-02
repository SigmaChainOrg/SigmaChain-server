import uuid
from datetime import timedelta
from typing import Any, Dict

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
        nullable=False,
    )
    form_pattern_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("workflow.form_pattern.form_pattern_id"),
        default=None,
        nullable=True,
    )
    next_activity_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("workflow.activity.activity_id"),
        default=None,
        nullable=True,
    )

    form_pattern: Mapped[FormPattern] = relationship(
        "FormPattern",
        back_populates="activity",
        uselist=False,
        init=False,
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "activity_id": self.activity_id,
            "label": self.label,
            "description": self.description,
            "estimated_time": self.estimated_time,
            "form_pattern_id": self.form_pattern_id,
            "next_activity_id": self.next_activity_id,
            "form_pattern": self.form_pattern.to_dict() if self.form_pattern else None,
        }


class ActivityAssignees(Base):
    __tablename__ = "activity_assignees"
    __table_args__ = {"schema": "workflow"}

    activity_assignee_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        init=False,
    )
    activity_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("workflow.activity.activity_id"),
        nullable=False,
    )
    assignee_type: Mapped[AssigneeEnum] = mapped_column(
        AssigneeEnumSQLA,
        nullable=False,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("access_control.user.user_id"),
        nullable=True,
    )
    group_id: Mapped[uuid.UUID] = mapped_column(
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

    def to_dict(self) -> Dict[str, Any]:
        return {
            "activity_assignee_id": self.activity_assignee_id,
            "activity_id": self.activity_id,
            "assignee_type": self.assignee_type.value,
            "user_id": self.user_id,
            "group_id": self.group_id,
            "user": self.user.to_dict() if self.user else None,
            "group": self.group.to_dict() if self.group else None,
        }
