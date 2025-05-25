from typing import List, Optional, Sequence
from uuid import UUID

from sqlalchemy import literal_column
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import aliased, selectinload

from src.database.models.access_control.group import Group
from src.database.models.access_control.user import User
from src.service_gateway.api.v1.schemas.access_control.group_schemas import (
    GroupAssignUserInput,
    GroupFilters,
    GroupInput,
    GroupQuery,
    GroupRead,
    GroupUpdate,
)
from src.service_gateway.api.v1.services.user_service import UserService
from src.utils.http_exceptions import BadRequestError


class GroupHierarchy:
    """Class to represent a Group(Model) hierarchy"""

    def __init__(
        self,
        group: Group,
        child_groups: Optional[List["GroupHierarchy"]] = None,
    ) -> None:
        self.group = group
        self.child_groups = child_groups if child_groups is not None else []

    def __repr__(self) -> str:
        return f"GroupHierarchy(group={self.group.name}, child_groups={len(self.child_groups)})"

    def to_group_read(self) -> GroupRead:
        return GroupRead(
            **self.group.to_dict(),
            child_groups=[group.to_group_read() for group in self.child_groups],
        )


class GroupService:
    def __init__(self, db: AsyncSession) -> None:
        self.db: AsyncSession = db

    ## Friendly methods

    async def _get_group_by_id(
        self,
        group_id: UUID,
        include_users: bool = False,
    ) -> Optional[Group]:
        query = select(Group).where(Group.group_id == group_id)

        if include_users:
            query = query.options(selectinload(Group.users).joinedload(User.user_info))

        result = await self.db.execute(query)
        group = result.scalars().first()

        return group

    async def _get_all_groups(
        self,
        include_users: bool = False,
        name_like: Optional[str] = None,
    ) -> Sequence[Group]:
        query = select(Group)

        if include_users:
            query = query.options(selectinload(Group.users).joinedload(User.user_info))

        if name_like:
            query = query.where(Group.name.ilike(f"%{name_like}%"))

        result = await self.db.execute(query)
        groups = result.scalars().all()

        return groups

    async def _get_group_with_children(
        self, group_id: UUID, include_users: bool = False
    ) -> Optional[GroupHierarchy]:
        """
        Recursively retrieves a group with all its children using SQLAlchemy CTE,
        without modifying the `Group` model, and returns a `GroupHierarchy`.
        """
        group_hierarchy_cte = (
            select(
                Group.group_id,
                Group.name,
                Group.parent_id,
                literal_column("0").label("depth"),
            )
            .where(Group.group_id == group_id)
            .cte(name="group_hierarchy", recursive=True)
        )

        parent_cte_alias = aliased(group_hierarchy_cte, name="parent_cte_alias")

        group_hierarchy_cte = group_hierarchy_cte.union_all(
            select(
                Group.group_id,
                Group.name,
                Group.parent_id,
                (parent_cte_alias.c.depth + 1).label("depth"),
            ).join(parent_cte_alias, Group.parent_id == parent_cte_alias.c.group_id)
        )

        stmt = select(Group).where(
            Group.group_id.in_(select(group_hierarchy_cte.c.group_id))
        )

        if include_users:
            stmt = stmt.options(selectinload(Group.users))

        result = await self.db.execute(stmt)
        groups = result.scalars().all()

        if not groups:
            return None

        groups_dict = {group.group_id: GroupHierarchy(group=group) for group in groups}

        for group_hierarchy in groups_dict.values():
            parent_id = group_hierarchy.group.parent_id

            if parent_id and parent_id in groups_dict:
                groups_dict[parent_id].child_groups.append(group_hierarchy)

        return groups_dict.get(group_id)

    ## Public methods

    async def get_groups(self, filters: GroupFilters) -> List[GroupRead]:
        groups = await self._get_all_groups(
            include_users=filters.include_users,
            name_like=filters.name,
        )

        if not groups:
            return []

        await self.db.flush()

        groups_dict = {
            group.group_id: GroupRead.model_validate(group.to_dict())
            for group in groups
        }

        for group in groups_dict.values():
            if group.parent_id is None:
                continue
            else:
                parent_group = groups_dict.get(group.parent_id)

                if parent_group is None:
                    continue

                if parent_group.child_groups is None:
                    parent_group.child_groups = []

                group.child_groups = []

                parent_group.child_groups.append(group)

        return [group for group in groups_dict.values() if group.parent_id is None]

    async def get_group(self, group_id: UUID, query: GroupQuery) -> GroupRead:
        group_read: Optional[GroupRead] = None

        if query.include_children:
            group_hierarchy = await self._get_group_with_children(
                group_id,
                include_users=query.include_users,
            )
            if group_hierarchy is not None:
                group_read = group_hierarchy.to_group_read()

        else:
            group = await self._get_group_by_id(
                group_id,
                include_users=query.include_users,
            )
            if group is not None:
                group_read = GroupRead.model_validate(group.to_dict())

        if group_read is None:
            raise BadRequestError("Group not found")

        return group_read

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
            group = await self._get_group_by_id(group_id)

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

    async def assign_user_to_group(self, input: GroupAssignUserInput) -> GroupRead:
        try:
            group = await self._get_group_by_id(input.group_id, include_users=True)

            if group is None:
                raise BadRequestError("User or Group not found")

            user_service = UserService(self.db)

            user = await user_service._get_user(by="id", value=input.user_id)

            if user is None:
                raise BadRequestError("User or Group not found")

            group.users.append(user)

            await self.db.flush()
            await self.db.refresh(group)

            group_read = GroupRead.model_validate(group.to_dict())

            await self.db.commit()

            return group_read

        except Exception:
            await self.db.rollback()
            raise
