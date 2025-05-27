from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, ForeignKey, Integer
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
    form_field_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("workflow.form_field.form_field_id", ondelete="SET NULL"),
        nullable=True,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        init=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False,
        init=False,
    )
    published_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        server_default=None,
        nullable=True,
        init=False,
    )

    activity: Mapped["Activity"] = relationship(
        "Activity",
        back_populates="form_pattern",
        uselist=False,
        init=False,
    )

    @property
    def is_published(self) -> bool:
        return self.published_at is not None
