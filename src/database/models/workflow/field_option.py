from __future__ import annotations

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from src.database.configuration import Base


class FieldOption(Base):
    __tablename__ = "field_option"
    __table_args__ = {"schema": "workflow"}

    field_option_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        init=False,
    )
    form_field_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("workflow.form_field.form_field_id", ondelete="CASCADE"),
        nullable=False,
    )
    title: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )
