import uuid

from sqlalchemy import UUID, Boolean, Column, DateTime, Enum, ForeignKey, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from src.database.configuration import Base
from src.database.models.access_control.enums import IdTypeEnum


class User(Base):
    __tablename__ = "user"
    __table_args__ = {"schema": "access_control"}

    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4())
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    user_info = relationship("UserInfo", back_populates="user", uselist=False)
    roles = relationship("UserRoles", back_populates="user")
    groups = relationship("UserGroups", back_populates="user")


class UserInfo(Base):
    __tablename__ = "user_info"
    __table_args__ = {"schema": "access_control"}

    user_info_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4())
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("access_control.user.user_id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    first_name = Column(String(255), nullable=False)
    last_name = Column(String(255), nullable=False)
    id_type = Column(
        Enum(
            IdTypeEnum,
            name="id_type_enum",
            schema="access_control",
        ),
        nullable=False,
    )
    id_number = Column(String(50), nullable=False)
    birth_date = Column(DateTime, nullable=False)
    updated_at = Column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    user = relationship("User", back_populates="user_info", uselist=False)
