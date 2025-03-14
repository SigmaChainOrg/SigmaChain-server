import uuid
from datetime import datetime

from sqlalchemy import UUID, Boolean, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from src.database.configuration import Base


class SecureCode(Base):
    __tablename__ = "secure_code"
    __table_args__ = {"schema": "access_control"}

    secure_code_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        nullable=False,
        default=uuid.uuid4,
        init=False,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("access_control.user.user_id", ondelete="CASCADE"),
        nullable=False,
    )
    code: Mapped[str] = mapped_column(
        String(6),
        nullable=False,
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
    )
    has_been_used: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    def to_dict(self):
        return {
            "secure_code_id": self.secure_code_id,
            "user_id": self.user_id,
            "code": self.code,
            "expires_at": self.expires_at,
            "has_been_used": self.has_been_used,
        }
