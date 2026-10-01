import os


class Config:
    SECRET_KEY = os.getenv(
        "SECRET_KEY",
        "change-me-in-production",
    )

    JWT_SECRET_KEY = os.getenv(
        "JWT_SECRET_KEY",
        "change-jwt-secret-in-production",
    )

    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg://shopapi:shopapi@localhost:5432/shopapi",
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    REDIS_URL = os.getenv(
        "REDIS_URL",
        "redis://localhost:6379/0",
    )

    CACHE_DEFAULT_TIMEOUT = int(
        os.getenv("CACHE_DEFAULT_TIMEOUT", "300")
    )

    DEBUG = os.getenv("FLASK_DEBUG", "false").lower() == "true"

    LOG_LEVEL = os.getenv(
        "LOG_LEVEL",
        "INFO",
    )

    JSON_SORT_KEYS = False

    PAGINATION_DEFAULT = int(
        os.getenv("PAGINATION_DEFAULT", "20")
    )

    PAGINATION_MAX = int(
        os.getenv("PAGINATION_MAX", "100")
    )
