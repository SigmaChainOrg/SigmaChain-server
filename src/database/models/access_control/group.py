from sqlalchemy import UUID, Column, ForeignKey, String
from sqlalchemy.orm import relationship

from src.database.configuration import Base


class UserGroups(Base):
    __tablename__ = "user_groups"
    __table_args__ = {"schema": "access_control"}

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("access_control.user.user_id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )
    group_id = Column(
        UUID(as_uuid=True),
        ForeignKey("access_control.group.group_id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )

    user = relationship("User", back_populates="groups")
    group = relationship("Group", back_populates="users")


class Group(Base):
    __tablename__ = "group"
    __table_args__ = {"schema": "access_control"}

    group_id = Column(UUID(as_uuid=True), primary_key=True, nullable=False)
    name = Column(String(255), nullable=False, unique=True)
    parent_id = Column(UUID(as_uuid=True), ForeignKey("access_control.group.group_id"))

    users = relationship("UserGroups", back_populates="group")
