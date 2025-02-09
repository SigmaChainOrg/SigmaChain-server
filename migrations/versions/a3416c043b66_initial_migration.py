"""Initial migration

Revision ID: a3416c043b66
Revises:
Create Date: 2025-02-09 11:42:14.259193

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "a3416c043b66"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS access_control")

    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "user",
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("hashed_password", sa.String(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("is_verified", sa.Boolean(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.PrimaryKeyConstraint("user_id"),
        schema="access_control",
    )
    op.create_index(
        op.f("ix_access_control_user_email"),
        "user",
        ["email"],
        unique=True,
        schema="access_control",
    )
    op.create_table(
        "user_info",
        sa.Column("user_info_id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("first_name", sa.String(length=255), nullable=False),
        sa.Column("last_name", sa.String(length=255), nullable=False),
        sa.Column(
            "id_type",
            sa.Enum(
                "ID_CARD", "PASSPORT", name="id_type_enum", schema="access_control"
            ),
            nullable=False,
        ),
        sa.Column("id_number", sa.String(length=50), nullable=False),
        sa.Column("birth_date", sa.DateTime(), nullable=False),
        sa.Column(
            "updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["user_id"], ["access_control.user.user_id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("user_info_id"),
        sa.UniqueConstraint("user_id"),
        schema="access_control",
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("user_info", schema="access_control")
    op.drop_index(
        op.f("ix_access_control_user_email"), table_name="user", schema="access_control"
    )
    op.drop_table("user", schema="access_control")
    # ### end Alembic commands ###
