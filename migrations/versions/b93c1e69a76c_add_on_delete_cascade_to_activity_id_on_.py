"""Add ON DELETE CASCADE to activity_id  on activity_assignees

Revision ID: b93c1e69a76c
Revises: 2fe832711654
Create Date: 2025-05-16 21:38:49.257183

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "b93c1e69a76c"
down_revision: Union[str, None] = "2fe832711654"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(
        "activity_assignees_activity_id_fkey",
        "activity_assignees",
        schema="workflow",
        type_="foreignkey",
    )
    op.create_foreign_key(
        None,
        "activity_assignees",
        "activity",
        ["activity_id"],
        ["activity_id"],
        source_schema="workflow",
        referent_schema="workflow",
        ondelete="CASCADE",
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(
        "activity_assignees_activity_id_fkey",
        "activity_assignees",
        schema="workflow",
        type_="foreignkey",
    )
    op.create_foreign_key(
        "activity_assignees_activity_id_fkey",
        "activity_assignees",
        "activity",
        ["activity_id"],
        ["activity_id"],
        source_schema="workflow",
        referent_schema="workflow",
    )
    # ### end Alembic commands ###
