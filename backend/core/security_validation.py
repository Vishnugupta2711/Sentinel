"""
Startup validation: refuse to start in production with insecure defaults.
This prevents accidental deployment with placeholder secrets.
"""
import sys
import structlog

logger = structlog.get_logger(__name__)

# Secrets that must never reach production unchanged
_INSECURE_PLACEHOLDERS = {
    "super-secret",
    "change-me-to-a-random-256-bit-key",
    "change-me-in-production",
    "securepassword",
    "password",
    "sk-placeholder",
    "pk.placeholder",
    "not-used",
    "",
}

_MIN_JWT_SECRET_LEN = 32


def _fail(message: str) -> None:
    logger.critical(f"[STARTUP ABORT] {message}")
    sys.exit(1)


def validate_secrets(settings) -> None:
    """
    Called during application startup. Aborts in production if any
    security-critical configuration is insecure.
    """
    from core.config import EnvironmentType
    if settings.app.environment != EnvironmentType.PRODUCTION:
        logger.warning(
            "Secret validation skipped — running in non-production mode.",
            environment=settings.app.environment.value,
        )
        return

    logger.info("Running production secret validation...")

    # JWT Secret
    jwt_secret = settings.security.jwt_secret
    if jwt_secret in _INSECURE_PLACEHOLDERS:
        _fail("SECURITY_JWT_SECRET is set to a placeholder value. Generate a secure 256-bit key.")
    if len(jwt_secret) < _MIN_JWT_SECRET_LEN:
        _fail(f"SECURITY_JWT_SECRET must be at least {_MIN_JWT_SECRET_LEN} characters. Got {len(jwt_secret)}.")

    # CORS — wildcard in production is a security risk
    if settings.security.cors_origins == ["*"]:
        logger.warning(
            "SECURITY_CORS_ORIGINS is set to wildcard '*'. "
            "Set explicit origins in production to prevent CSRF."
        )

    # Allowed Hosts — wildcard in production
    if settings.security.allowed_hosts == ["*"]:
        logger.warning(
            "SECURITY_ALLOWED_HOSTS is set to wildcard '*'. "
            "Set explicit hostnames to prevent host header injection."
        )

    # Database credentials
    if settings.db.url and any(p in settings.db.url for p in ["change-me", "securepassword", "password"]):
        _fail("DATABASE_URL contains placeholder credentials. Update before deploying.")

    # Grafana / Neo4j passwords flow through env — check Neo4j
    neo4j_pw = settings.neo4j.password
    if neo4j_pw in _INSECURE_PLACEHOLDERS:
        _fail("NEO4J_PASSWORD is set to a placeholder. Update before deploying.")

    # Debug mode must be off
    if settings.app.debug:
        _fail("APP_DEBUG=true is not permitted in production.")

    logger.info("✓ Secret validation passed. All production secrets are non-default.")
