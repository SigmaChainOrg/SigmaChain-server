from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import UUID

from isodate import duration_isoformat


def serialize_datetime(dt: Optional[datetime]) -> Optional[str]:
    if dt is None:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    else:
        dt = dt.astimezone(timezone.utc)
    return dt.strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def serialize_timedelta(td: Optional[timedelta]) -> Optional[str]:
    if td is None:
        return None
    return duration_isoformat(td)


def serialize_uuid(uuid_value: Optional[UUID]) -> Optional[str]:
    return str(uuid_value) if uuid_value else None
    return str(uuid_value) if uuid_value else None
