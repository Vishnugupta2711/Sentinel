from typing import Generator

from core.config import Settings, settings


def get_settings() -> Generator[Settings, None, None]:
    """Dependency to inject application settings."""
    yield settings
