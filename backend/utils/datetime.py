from datetime import timezone, datetime


def utc_now() -> datetime:
    """Returns the current UTC datetime."""
    return datetime.now(timezone.utc)


def format_iso(dt: datetime) -> str:
    """Formats a datetime object to ISO 8601 string."""
    return dt.isoformat()
