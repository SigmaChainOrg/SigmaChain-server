from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.database.models.access_control.group import Group
from src.service_gateway.api.v1.schemas.access_control.group_schemas import (
    GroupInput,
    GroupRead,
    GroupUpdate,
)
from src.utils.http_exceptions import BadRequestError


class GroupService:
    def __init__(self, db: AsyncSession) -> None:
        self.db: AsyncSession = db

    async def get_groups(self) -> list[GroupRead]:
        response = await self.db.execute(select(Group))
        groups = response.scalars().all()

        if not groups:
            return []

        groups_dict = {
            group.group_id: GroupRead.model_validate(group) for group in groups
        }

        for group in groups_dict.values():
            if group.parent_id:
                parent_group = groups_dict.get(group.parent_id)

                if parent_group is None:
                    continue

                if parent_group.child_groups is None:
                    parent_group.child_groups = []

                parent_group.child_groups.append(group)

        return [group for group in groups_dict.values() if group.parent_id is None]

    async def create_group(self, input: GroupInput) -> GroupRead:
        try:
            new_group = Group(**input.model_dump())
            self.db.add(new_group)

            await self.db.flush()
            await self.db.refresh(new_group)

            group_schema = GroupRead.model_validate(new_group)

            await self.db.commit()

            return group_schema

        except Exception:
            await self.db.rollback()
            raise

    async def update_group(self, group_id: UUID, input: GroupUpdate) -> GroupRead:
        try:
            result = await self.db.execute(
                select(Group).filter(Group.group_id == group_id)
            )

            group = result.scalars().first()

            if group is None:
                raise BadRequestError("Group not found")

            group_update_data = input.model_dump(exclude_unset=True)

            for key, value in group_update_data.items():
                setattr(group, key, value)

            await self.db.refresh(group)

            group_read = GroupRead.model_validate(group)

            await self.db.commit()

            return group_read

        except Exception:
            await self.db.rollback()
            raise
