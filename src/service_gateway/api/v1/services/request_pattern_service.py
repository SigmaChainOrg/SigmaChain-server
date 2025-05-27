from collections import Counter
from typing import List, Optional, Sequence
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from src.database.models.workflow.activity import Activity, ActivityAssignees
from src.database.models.workflow.enums import AssigneeEnum
from src.database.models.workflow.request_pattern import RequestPattern
from src.service_gateway.api.v1.schemas.workflow.form_pattern_schemas import (
    FormPatternInput,
    FormPatternRead,
)
from src.service_gateway.api.v1.schemas.workflow.request_pattern_schemas import (
    RequestPatternFilters,
    RequestPatternInput,
    RequestPatternQuery,
    RequestPatternRead,
    RequestPatternUpdate,
)
from src.service_gateway.api.v1.services.activity_service import ActivityService
from src.service_gateway.api.v1.services.form_pattern_service import FormPatternService
from src.service_gateway.api.v1.services.group_service import GroupService
from src.utils.http_exceptions import BadRequestError, NotFoundError


class RequestPatternService:
    def __init__(self, db: AsyncSession):
        self.db = db

    ## Friendly methods

    async def _get_request_pattern_by_id(
        self,
        request_pattern_id: UUID,
        include_groups: bool = False,
    ) -> Optional[RequestPattern]:
        stmt = select(RequestPattern).where(
            RequestPattern.request_pattern_id == request_pattern_id
        )

        if include_groups:
            stmt = stmt.options(selectinload(RequestPattern.groups))

        result = await self.db.execute(stmt)
        request_pattern = result.scalars().first()

        return request_pattern

    async def _get_request_patterns(
        self,
        label: Optional[str] = None,
        supervisor_id: Optional[UUID] = None,
        is_published: Optional[bool] = None,
        is_active: Optional[bool] = None,
        include_groups: bool = False,
    ) -> Sequence[RequestPattern]:
        stmt = select(RequestPattern)

        if label:
            stmt = stmt.where(RequestPattern.label.ilike(f"%{label}%"))

        if supervisor_id:
            stmt = stmt.where(RequestPattern.supervisor_id == supervisor_id)

        if is_published is not None:
            if is_published:
                stmt = stmt.where(RequestPattern.published_at.isnot(None))
            else:
                stmt = stmt.where(RequestPattern.published_at.is_(None))

        if is_active is not None:
            stmt = stmt.where(RequestPattern.is_active.is_(is_active))

        if include_groups:
            stmt = stmt.options(selectinload(RequestPattern.groups))

        result = await self.db.execute(stmt)
        request_patterns = result.scalars().all()

        return request_patterns

    ## Public methods

    async def create_request_pattern(
        self, input: RequestPatternInput
    ) -> RequestPatternRead:
        activity_service = ActivityService(self.db)

        try:
            activities_input = sorted(input.activities, key=lambda x: x.activity_order)

            first_activity_id: int = 0
            last_activity: Optional[Activity] = None

            if len(activities_input) == 0:
                raise BadRequestError(
                    "At least one activity with 'requester' assignee is required"
                )

            if len(activities_input) != len(
                set((activity.activity_order for activity in input.activities))
            ):
                raise BadRequestError("Activity order must have unique orders.")

            for i, activity_input in enumerate(activities_input):
                if i != activity_input.activity_order:
                    raise BadRequestError(
                        f"Activity order must be continuous. Found {activity_input.activity_order} and {i}"
                    )

                new_activity = Activity(
                    label=activity_input.label,
                    description=activity_input.description,
                )

                if activity_input.estimated_time:
                    new_activity.estimated_time = activity_input.estimated_time

                self.db.add(new_activity)
                await self.db.flush()
                await self.db.refresh(new_activity)

                assignee_input = activity_input.assignee

                if assignee_input:
                    activity_assignee = ActivityAssignees(
                        activity_id=new_activity.activity_id,
                        assignee_type=assignee_input.assignee_type,
                        user_id=assignee_input.user_id,
                        group_id=assignee_input.group_id,
                    )

                    new_activity.assignee = activity_assignee
                    await self.db.flush()
                    await self.db.refresh(activity_assignee)

                if last_activity:
                    last_activity.next_activity_id = new_activity.activity_id

                if i == 0:
                    first_activity_id = new_activity.activity_id

                    if not activity_input.assignee:
                        raise BadRequestError(
                            f"Assignee is required for the first activity {activity_input.label}"
                        )
                    if activity_input.assignee.assignee_type != AssigneeEnum.REQUESTER:
                        raise BadRequestError(
                            f"Assignee type must be 'requester' for the first activity {activity_input.label}"
                        )

                last_activity = new_activity

                await self.db.flush()
                await self.db.refresh(new_activity)

            request_pattern = RequestPattern(
                label=input.label,
                description=input.description,
                supervisor_id=input.supervisor_id,
                activity_id=first_activity_id,
                published_at=None,
            )

            group_service = GroupService(self.db)

            for group_id in input.groups:
                group = await group_service._get_group_by_id(group_id)

                if not group:
                    raise BadRequestError(f"Group with id {group_id} not found")

                request_pattern.groups.append(group)
            else:
                request_pattern.groups = []

            self.db.add(request_pattern)
            await self.db.flush()
            await self.db.refresh(
                request_pattern, attribute_names=["groups", "supervisor"]
            )

            activities_chain = await activity_service._get_activities_chain(
                first_activity_id=request_pattern.activity_id
            )

            request_pattern_dict = request_pattern.to_dict()
            request_pattern_dict["activities"] = activities_chain.to_activities_read()

            request_pattern_read = RequestPatternRead.model_validate(
                request_pattern_dict
            )

            await self.db.commit()

            return request_pattern_read

        except Exception:
            await self.db.rollback()
            raise

    async def get_request_pattern(
        self, request_pattern_id: UUID, query: RequestPatternQuery
    ) -> RequestPatternRead:
        activity_service = ActivityService(self.db)

        request_pattern = await self._get_request_pattern_by_id(
            request_pattern_id=request_pattern_id,
            include_groups=query.include_groups,
        )

        if not request_pattern:
            raise NotFoundError(
                f"Request pattern with id {request_pattern_id} not found"
            )

        if query.include_activities:
            activities_chain = await activity_service._get_activities_chain(
                first_activity_id=request_pattern.activity_id
            )
        else:
            activities_chain = None

        request_pattern_dict = request_pattern.to_dict()

        if activities_chain is not None:
            request_pattern_dict["activities"] = activities_chain.to_activities_read()

        request_pattern_read = RequestPatternRead.model_validate(request_pattern_dict)

        return request_pattern_read

    async def get_request_patterns(
        self,
        filters: RequestPatternFilters,
    ) -> List[RequestPatternRead]:
        activity_service = ActivityService(self.db)

        request_patterns = await self._get_request_patterns(
            label=filters.label,
            supervisor_id=filters.supervisor_id,
            is_published=filters.is_published,
            is_active=filters.is_active,
            include_groups=filters.include_groups,
        )

        if filters.include_activities:
            request_patterns_read = []

            for request_pattern in request_patterns:
                activities_chain = await activity_service._get_activities_chain(
                    first_activity_id=request_pattern.activity_id
                )

                request_pattern_dict = request_pattern.to_dict()
                request_pattern_dict["activities"] = (
                    activities_chain.to_activities_read()
                )

                request_patterns_read.append(
                    RequestPatternRead.model_validate(
                        request_pattern_dict, strict=False
                    )
                )
        else:
            request_patterns_read = [
                RequestPatternRead.model_validate(request_pattern.to_dict())
                for request_pattern in request_patterns
            ]

        return request_patterns_read

    async def update_request_pattern(
        self, request_pattern_id: UUID, update: RequestPatternUpdate
    ) -> RequestPatternRead:
        activity_service = ActivityService(self.db)

        try:
            request_pattern = await self._get_request_pattern_by_id(request_pattern_id)
            if request_pattern is None:
                raise BadRequestError("Request pattern not found")

            if request_pattern.is_published:
                raise BadRequestError("Cannot update a published request pattern.")

            update_data = update.model_dump(exclude_unset=True)

            # A. Update simple fields if provided
            for attr in ("label", "description", "supervisor_id"):
                if attr in update_data:
                    setattr(request_pattern, attr, update_data[attr])

            # B. Update groups if provided
            if update.groups:
                request_pattern.groups.clear()
                group_service = GroupService(self.db)
                for group_id in update.groups:
                    group = await group_service._get_group_by_id(group_id)
                    if not group:
                        raise BadRequestError(f"Group with id {group_id} not found")
                    request_pattern.groups.append(group)

            # C. Replace activity chain if provided
            if update.activities:
                activities_update = sorted(
                    update.activities, key=lambda x: x.activity_order
                )

                if not activities_update:
                    raise BadRequestError(
                        "At least one activity with 'requester' assignee is required"
                    )

                if len(activities_update) != len(
                    set(a.activity_order for a in activities_update)
                ):
                    raise BadRequestError("Activity order must be unique")

                # 1. Get actual activitie chain
                last_activities_chain = await activity_service._get_activities_chain(
                    first_activity_id=request_pattern.activity_id
                )

                # 2. Validate activities
                ids_to_update = [
                    a.activity_id for a in activities_update if a.activity_id
                ]
                changes_ids = (
                    last_activities_chain.get_activity_ids_to_update_or_delete(
                        activities_to_update=ids_to_update
                    )
                )

                if Counter(ids_to_update) != Counter(changes_ids.get("update", [])):
                    raise BadRequestError(
                        "Activity ids to update must be unique and match the existing activities"
                    )

                if Counter(update.activities_to_delete) != Counter(
                    changes_ids.get("delete", [])
                ):
                    raise BadRequestError(
                        "Activity ids to delete must be unique and match the existing activities"
                    )

                # 3. Delete activities if provided
                for activity_id in update.activities_to_delete:
                    activity_to_delete = last_activities_chain.get_activity_by_id(
                        activity_id
                    )
                    if not activity_to_delete:
                        raise BadRequestError(
                            f"Activity with id {activity_id} not found"
                        )

                    await self.db.delete(activity_to_delete)

                await self.db.flush()

                # 4. Create new activity chain
                first_activity_id = 0
                last_activity = None

                for i, activity_update in enumerate(activities_update):
                    if i != activity_update.activity_order:
                        raise BadRequestError(
                            f"Activity order must be continuous. Found {activity_update.activity_order} and {i}"
                        )

                    activity_to_order: Optional[Activity] = None

                    if activity_update.activity_id:
                        activity_on_pattern = last_activities_chain.get_activity_by_id(
                            activity_update.activity_id
                        )

                        if not activity_on_pattern:
                            raise BadRequestError(
                                f"Activity with id {activity_update.activity_id} not found on Request-Pattern"
                            )

                        # Update simple activity fields if provided
                        if activity_update.label:
                            activity_on_pattern.label = activity_update.label

                        if activity_update.description:
                            activity_on_pattern.description = (
                                activity_update.description
                            )

                        if activity_update.estimated_time:
                            activity_on_pattern.estimated_time = (
                                activity_update.estimated_time
                            )

                        if activity_update.assignee:
                            if activity_on_pattern.assignee:
                                activity_on_pattern.assignee.assignee_type = (
                                    activity_update.assignee.assignee_type
                                )
                                activity_on_pattern.assignee.user_id = (
                                    activity_update.assignee.user_id
                                )
                                activity_on_pattern.assignee.group_id = (
                                    activity_update.assignee.group_id
                                )
                            else:
                                activity_on_pattern.assignee = ActivityAssignees(
                                    activity_id=activity_on_pattern.activity_id,
                                    assignee_type=activity_update.assignee.assignee_type,
                                    user_id=activity_update.assignee.user_id,
                                    group_id=activity_update.assignee.group_id,
                                )

                            await self.db.flush()
                            await self.db.refresh(activity_on_pattern.assignee)

                        activity_on_pattern.next_activity_id = None
                        activity_to_order = activity_on_pattern

                    else:
                        if not (activity_update.label and activity_update.description):
                            raise BadRequestError(
                                "New activity must have label and description"
                            )

                        new_activity = Activity(
                            label=activity_update.label,
                            description=activity_update.description,
                        )
                        if activity_update.estimated_time:
                            new_activity.estimated_time = activity_update.estimated_time

                        self.db.add(new_activity)

                        await self.db.flush()
                        await self.db.refresh(new_activity)

                        if activity_update.assignee:
                            assignee = ActivityAssignees(
                                activity_id=new_activity.activity_id,
                                assignee_type=activity_update.assignee.assignee_type,
                                user_id=activity_update.assignee.user_id,
                                group_id=activity_update.assignee.group_id,
                            )
                            new_activity.assignee = assignee
                            await self.db.flush()
                            await self.db.refresh(assignee)

                        activity_to_order = new_activity

                    if last_activity:
                        last_activity.next_activity_id = activity_to_order.activity_id
                        await self.db.flush()
                        await self.db.refresh(last_activity)

                    if i == 0:
                        if not activity_to_order.assignee:
                            raise BadRequestError(
                                f"Assignee is required for the first activity '{activity_update.label}'"
                            )
                        if (
                            activity_to_order.assignee.assignee_type
                            != AssigneeEnum.REQUESTER
                        ):
                            raise BadRequestError(
                                f"Assignee type must be 'requester' for the first activity '{activity_update.label}'"
                            )
                        first_activity_id = activity_to_order.activity_id

                    last_activity = activity_to_order

                if last_activity is not None:
                    last_activity.next_activity_id = None

                request_pattern.activity_id = first_activity_id

            # D. Return the updated request pattern
            await self.db.flush()
            await self.db.refresh(
                request_pattern, attribute_names=["groups", "supervisor"]
            )

            activities_chain = await activity_service._get_activities_chain(
                first_activity_id=request_pattern.activity_id
            )
            request_pattern_dict = request_pattern.to_dict()
            request_pattern_dict["activities"] = activities_chain.to_activities_read()

            result = RequestPatternRead.model_validate(request_pattern_dict)
            await self.db.commit()
            return result

        except Exception:
            await self.db.rollback()
            raise

    async def create_form_pattern_for_activity(
        self,
        request_pattern_id: UUID,
        activity_id: int,
        input: FormPatternInput,
    ) -> FormPatternRead:
        try:
            form_pattern_service = FormPatternService(self.db)
            activity_service = ActivityService(self.db)

            request_pattern = await self._get_request_pattern_by_id(request_pattern_id)
            if not request_pattern:
                raise NotFoundError(
                    f"Request pattern with id {request_pattern_id} not found"
                )

            activity = await activity_service._get_activity_from_activity_chain(
                first_activity_id=request_pattern.activity_id,
                target_activity_id=activity_id,
            )

            if not activity:
                raise NotFoundError(
                    f"Activity with id {activity_id} not found in request pattern"
                )

            await self.db.refresh(activity, attribute_names=["form_pattern"])

            if activity.form_pattern:
                raise BadRequestError(
                    f"Activity with id {activity_id} already has a form pattern"
                )

            form_pattern = (
                await form_pattern_service._create_form_pattern_without_commit(
                    input=input,
                )
            )

            activity.form_pattern = form_pattern

            await self.db.flush()
            await self.db.refresh(activity, attribute_names=["form_pattern"])

            fields_chain = await form_pattern_service._get_form_fields_chain(
                first_field_id=form_pattern.form_field_id
            )

            form_pattern_read = FormPatternRead.model_validate(
                dict(
                    **activity.form_pattern.to_dict(),
                    fields=fields_chain._to_fields_read(),
                ),
            )

            await self.db.commit()

            return form_pattern_read

        except Exception:
            await self.db.rollback()
            raise
