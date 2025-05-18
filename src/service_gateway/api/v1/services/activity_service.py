from typing import Dict, List, Literal, Optional

from sqlalchemy import literal_column
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import aliased

from src.database.models.workflow.activity import Activity
from src.service_gateway.api.v1.schemas.workflow.activity_schemas import ActivityRead


class ActivitiesChain:
    """Class to represent a chain of activities"""

    def __init__(self) -> None:
        self.activities: Dict[int, Activity] = {}

    def add_activity(self, activity: Activity) -> None:
        count = len(self.activities) + 1
        self.activities[count] = activity

    def to_activities_read(self) -> List[ActivityRead]:
        return [
            ActivityRead.model_validate(
                dict(
                    **activity.__dict__,
                    activity_order=key,
                )
            )
            for key, activity in self.activities.items()
        ]

    def get_activity_by_order(self, order: int) -> Optional[Activity]:
        return self.activities.get(order)

    def get_activity_by_id(self, activity_id: int) -> Optional[Activity]:
        for activity in self.activities.values():
            if activity.activity_id == activity_id:
                return activity
        return None

    def get_activity_ids_to_update_or_delete(
        self, activities_to_update: List[int]
    ) -> Dict[Literal["update", "delete"], List[int]]:
        activities_on_chain_to_update = []
        activities_on_chain_to_delete = []

        for activity in self.activities.values():
            if activity.activity_id in activities_to_update:
                activities_on_chain_to_update.append(activity.activity_id)
            else:
                activities_on_chain_to_delete.append(activity.activity_id)

        return {
            "update": activities_on_chain_to_update,
            "delete": activities_on_chain_to_delete,
        }


class ActivityService:
    def __init__(self, db: AsyncSession):
        self.db = db

    ## Friendly methods

    async def _get_activities_chain(
        self,
        first_activity_id: int,
    ) -> ActivitiesChain:
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

        activities_chain = ActivitiesChain()

        for activity, order in result.all():
            await self.db.refresh(activity, attribute_names=["assignee"])

            if activity.assignee:
                await self.db.refresh(
                    activity.assignee, attribute_names=["user", "group"]
                )

            activities_chain.add_activity(activity)

        return activities_chain
