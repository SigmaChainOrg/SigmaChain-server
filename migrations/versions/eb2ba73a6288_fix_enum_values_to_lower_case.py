"""Changing upper_case enums to lower_case

Revision ID: eb2ba73a6288
Revises: 2fe7d0e6c141
Create Date: 2025-02-24 19:36:28.584017

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "eb2ba73a6288"
down_revision: Union[str, None] = "2fe7d0e6c141"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# New ENUM values in lowercase
new_role_values = ("requester", "reviewer", "supervisor", "manager")
new_resource_values = ("own_requests", "all_requests", "own_patterns", "all_patterns")
new_operation_values = ("create", "read", "update", "delete")
new_id_type_values = ("id_card", "passport")


def upgrade() -> None:
    # Temporarily convert all columns using the ENUM to TEXT
    for enum_name, values, table_name, column_name in [
        ("role_enum", new_role_values, "user_roles", "role"),
        ("role_enum", new_role_values, "policy", "role"),
        ("resource_enum", new_resource_values, "policy", "resource"),
        ("operation_enum", new_operation_values, "policy", "operation"),
        ("id_type_enum", new_id_type_values, "user_info", "id_type"),
    ]:
        op.execute(
            f"ALTER TABLE access_control.{table_name} ALTER COLUMN {column_name} TYPE TEXT USING {column_name}::TEXT"
        )

    # Update the data to match the new ENUM values (convert to lowercase)
    op.execute("UPDATE access_control.user_roles SET role = LOWER(role)")
    op.execute("UPDATE access_control.policy SET role = LOWER(role)")
    op.execute("UPDATE access_control.policy SET resource = LOWER(resource)")
    op.execute("UPDATE access_control.policy SET operation = LOWER(operation)")
    op.execute("UPDATE access_control.user_info SET id_type = LOWER(id_type)")

    # Drop all enums now that columns are TEXT
    op.execute("DROP TYPE IF EXISTS access_control.role_enum CASCADE")
    op.execute("DROP TYPE IF EXISTS access_control.resource_enum CASCADE")
    op.execute("DROP TYPE IF EXISTS access_control.operation_enum CASCADE")
    op.execute("DROP TYPE IF EXISTS access_control.id_type_enum CASCADE")

    # Recreate enums with lowercase values
    op.execute(f"CREATE TYPE access_control.role_enum AS ENUM {new_role_values}")
    op.execute(
        f"CREATE TYPE access_control.resource_enum AS ENUM {new_resource_values}"
    )
    op.execute(
        f"CREATE TYPE access_control.operation_enum AS ENUM {new_operation_values}"
    )
    op.execute(f"CREATE TYPE access_control.id_type_enum AS ENUM {new_id_type_values}")

    # Restore columns to the new ENUM type
    for enum_name, table_name, column_name in [
        ("role_enum", "user_roles", "role"),
        ("role_enum", "policy", "role"),
        ("resource_enum", "policy", "resource"),
        ("operation_enum", "policy", "operation"),
        ("id_type_enum", "user_info", "id_type"),
    ]:
        op.execute(
            f"ALTER TABLE access_control.{table_name} ALTER COLUMN {column_name} TYPE access_control.{enum_name} USING {column_name}::access_control.{enum_name}"
        )


def downgrade() -> None:
    # Convert all ENUM columns back to TEXT before dropping the ENUM types
    for enum_name, table_name, column_name in [
        ("role_enum", "user_roles", "role"),
        ("role_enum", "policy", "role"),
        ("resource_enum", "policy", "resource"),
        ("operation_enum", "policy", "operation"),
        ("id_type_enum", "user_info", "id_type"),
    ]:
        op.execute(
            f"ALTER TABLE access_control.{table_name} ALTER COLUMN {column_name} TYPE TEXT USING {column_name}::TEXT"
        )

    # Update data back to uppercase values to match the old ENUM format
    op.execute("UPDATE access_control.user_roles SET role = UPPER(role)")
    op.execute("UPDATE access_control.policy SET role = UPPER(role)")
    op.execute("UPDATE access_control.policy SET resource = UPPER(resource)")
    op.execute("UPDATE access_control.policy SET operation = UPPER(operation)")
    op.execute("UPDATE access_control.user_info SET id_type = UPPER(id_type)")

    # Drop the lowercase ENUMs
    op.execute("DROP TYPE IF EXISTS access_control.role_enum CASCADE")
    op.execute("DROP TYPE IF EXISTS access_control.resource_enum CASCADE")
    op.execute("DROP TYPE IF EXISTS access_control.operation_enum CASCADE")
    op.execute("DROP TYPE IF EXISTS access_control.id_type_enum CASCADE")

    # Restore original ENUMs (assuming uppercase values were used previously)
    old_role_values = "('REQUESTER', 'REVIEWER', 'SUPERVISOR', 'MANAGER')"
    old_resource_values = (
        "('OWN_REQUESTS', 'ALL_REQUESTS', 'OWN_PATTERNS', 'ALL_PATTERNS')"
    )
    old_operation_values = "('CREATE', 'READ', 'UPDATE', 'DELETE')"
    old_id_type_values = "('ID_CARD', 'PASSPORT')"

    op.execute(f"CREATE TYPE access_control.role_enum AS ENUM {old_role_values}")
    op.execute(
        f"CREATE TYPE access_control.resource_enum AS ENUM {old_resource_values}"
    )
    op.execute(
        f"CREATE TYPE access_control.operation_enum AS ENUM {old_operation_values}"
    )
    op.execute(f"CREATE TYPE access_control.id_type_enum AS ENUM {old_id_type_values}")

    # Restore columns to the original ENUM type
    for enum_name, table_name, column_name in [
        ("role_enum", "user_roles", "role"),
        ("role_enum", "policy", "role"),
        ("resource_enum", "policy", "resource"),
        ("operation_enum", "policy", "operation"),
        ("id_type_enum", "user_info", "id_type"),
    ]:
        op.execute(
            f"ALTER TABLE access_control.{table_name} ALTER COLUMN {column_name} TYPE access_control.{enum_name} USING {column_name}::access_control.{enum_name}"
        )
