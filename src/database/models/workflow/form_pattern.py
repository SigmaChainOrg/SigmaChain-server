from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict

from sqlalchemy import DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from src.database.configuration import Base

if TYPE_CHECKING:
    from src.database.models.workflow.activity import Activity


class FormPattern(Base):
    __tablename__ = "form_pattern"
    __table_args__ = {"schema": "workflow"}

    form_pattern_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        init=False,
    )
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        init=False,
    )
    created_at: Mapped[DateTime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False,
        init=False,
    )

    activity: Mapped["Activity"] = relationship(
        "Activity",
        back_populates="form_pattern",
        uselist=False,
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "form_pattern_id": self.form_pattern_id,
            "updated_at": self.updated_at,
            "created_at": self.created_at,
            "activity": self.activity.to_dict() if self.activity else None,
        }
