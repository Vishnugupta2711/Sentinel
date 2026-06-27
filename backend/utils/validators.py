import re


def is_valid_uuid(val: str) -> bool:
    """Basic check to see if string is a valid UUID."""
    pattern = re.compile(
        r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$", re.I
    )
    return bool(pattern.match(val))
