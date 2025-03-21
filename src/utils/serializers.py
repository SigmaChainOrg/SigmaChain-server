from datetime import datetime, timezone
from typing import Optional
from uuid import UUID


def serialize_datetime(dt: datetime):
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    else:
        dt = dt.astimezone(timezone.utc)
    return dt.strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def serialize_uuid(uuid_value: Optional[UUID]) -> Optional[str]:
    return str(uuid_value) if uuid_value else None
