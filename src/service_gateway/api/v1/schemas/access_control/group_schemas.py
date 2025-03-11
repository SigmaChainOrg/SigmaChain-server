from __future__ import annotations

from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_serializer

from src.utils.serializers import serialize_uuid


class GroupBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    group_id: UUID
    name: str

    @field_serializer("group_id")
    def serialize_group_uuid(self, group_id: UUID, _info):
        return serialize_uuid(group_id)


class GroupRead(GroupBase):
    parent_id: Optional[UUID] = None
    child_groups: Optional[List["GroupRead"]] = Field(
        None,
        description="List of child groups, Recursive structure",
        examples=[
            [
                {
                    "group_id": "123e4567-e89b-12d3-a456-426614174000",
                    "name": "Child Group",
                    "parent_id": "123e4567-e89b-12d3-a456-426614174001",
                    "child_groups": [],
                },
            ],
        ],
    )

    @field_serializer("parent_id")
    def serialize_parent_uuid(self, parent_id: Optional[UUID], _info):
        return serialize_uuid(parent_id)


class GroupInput(BaseModel):
    name: str
    parent_id: Optional[UUID] = None


class GroupUpdate(BaseModel):
    name: Optional[str] = None
    parent_id: Optional[UUID] = None
