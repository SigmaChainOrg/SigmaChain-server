from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlalchemy import literal_column
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import aliased

from src.database.models.workflow.activity import Activity, ActivityAssignees
from src.database.models.workflow.enums import AssigneeEnum
from src.database.models.workflow.request_pattern import RequestPattern
from src.service_gateway.api.v1.schemas.workflow.activity_schemas import ActivityRead
from src.service_gateway.api.v1.schemas.workflow.request_pattern_schemas import (
    RequestPatternInput,
    RequestPatternRead,
)
from src.service_gateway.api.v1.services.group_service import GroupService
from src.utils.http_exceptions import BadRequestError, NotFoundError


class ActivityOrder:
    """Class to represent a Activity(Model) with order"""

    def __init__(
        self,
        activity: Activity,
        activity_order: int,
    ) -> None:
        self.activity = activity
        self.activity_order = activity_order

    def to_dict(self) -> Dict[str, Any]:
        return {
            **self.activity.__dict__,
            "activity_order": self.activity_order,
        }


class RequestPatternService:
    def __init__(self, db: AsyncSession):
        self.db = db

    ## Friendly methods

    async def _get_request_pattern_by_id(
        self, request_pattern_id: UUID
    ) -> Optional[RequestPattern]:
        stmt = select(RequestPattern).where(
            RequestPattern.request_pattern_id == request_pattern_id
        )

        result = await self.db.execute(stmt)
        request_pattern = result.scalars().first()

        return request_pattern

    async def _get_activities_chain(
        self,
        first_activity_id: int,
    ) -> List[ActivityOrder]:
        activity_cte = (
            select(Activity)
            .add_columns(literal_column("1").label("order"))
            .where(Activity.activity_id == first_activity_id)
            .cte(name="activity_chain", recursive=True)
        )

        cte_alias = aliased(activity_cte, name="cte_alias")

        activity_cte = activity_cte.union_all(
            select(Activity)
            .add_columns((cte_alias.c.order + 1).label("order"))
            .join(cte_alias, Activity.activity_id == cte_alias.c.next_activity_id)
        )

        stmt = (
            select(Activity, activity_cte.c.order)
            .join(activity_cte, Activity.activity_id == activity_cte.c.activity_id)
            .order_by(activity_cte.c.order)
        )

        result = await self.db.execute(stmt)

        activities_ordered = []

        for activity, order in result.all():
            await self.db.refresh(activity, attribute_names=["assignee"])
            await self.db.refresh(activity.assignee, attribute_names=["user", "group"])

            activity_order = ActivityOrder(activity=activity, activity_order=order)
            activities_ordered.append(activity_order)

        return activities_ordered

    ## Public methods

    async def create_request_pattern(
        self, input: RequestPatternInput
    ) -> RequestPatternRead:
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
                raise BadRequestError("Activity order must be unique")

            for i, activity_input in enumerate(activities_input):
                if (i + 1) != activity_input.activity_order:
                    raise BadRequestError(
                        f"Activity order must be continuous. Found {activity_input.activity_order} and {i + 1}"
                    )

                new_activity = Activity(
                    label=activity_input.label,
                    description=activity_input.description,
                )

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

            activities_chain = await self._get_activities_chain(
                first_activity_id=request_pattern.activity_id
            )

            request_pattern_dict = request_pattern.__dict__
            request_pattern_dict["activities"] = [
                ActivityRead.model_validate(activity.to_dict())
                for activity in activities_chain
            ]

            request_pattern_read = RequestPatternRead.model_validate(
                request_pattern_dict
            )

            await self.db.commit()

            return request_pattern_read

        except Exception:
            await self.db.rollback()
            raise

    async def get_request_pattern(self, request_pattern_id: UUID) -> RequestPatternRead:
        request_pattern = await self._get_request_pattern_by_id(request_pattern_id)

        if not request_pattern:
            raise NotFoundError(
                f"Request pattern with id {request_pattern_id} not found"
            )

        await self.db.refresh(request_pattern)

        activities_chain = await self._get_activities_chain(
            first_activity_id=request_pattern.activity_id
        )

        request_pattern_dict = request_pattern.__dict__
        request_pattern_dict["activities"] = [
            ActivityRead.model_validate(activity.to_dict())
            for activity in activities_chain
        ]

        request_pattern_read = RequestPatternRead.model_validate(request_pattern_dict)

        return request_pattern_read
