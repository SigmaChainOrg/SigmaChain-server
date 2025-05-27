from __future__ import annotations

from typing import Optional

from sqlalchemy import Boolean, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.configuration import Base
from src.database.models.workflow.enums import InputTypeEnum, InputTypeEnumSQLA
from src.database.models.workflow.field_option import FieldOption


class FormField(Base):
    __tablename__ = "form_field"
    __table_args__ = {"schema": "workflow"}

    form_field_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        init=False,
    )
    input_type: Mapped[InputTypeEnum] = mapped_column(
        InputTypeEnumSQLA,
        nullable=False,
    )
    title: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )
    description: Mapped[Optional[str]] = mapped_column(
        String,
        nullable=True,
        default=None,
    )
    is_mandatory: Mapped[Optional[bool]] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )
    next_field_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("workflow.form_field.form_field_id", ondelete="SET NULL"),
        nullable=True,
        default=None,
    )

    options: Mapped[list[FieldOption]] = relationship(
        "FieldOption",
        foreign_keys=[FieldOption.form_field_id],
        uselist=True,
        init=False,
    )
