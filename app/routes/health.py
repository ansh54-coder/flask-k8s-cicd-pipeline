from flask import Blueprint

from app.extensions import db
from app.services.cache import ping as redis_ping


health_bp = Blueprint(
    "health",
    __name__,
)


@health_bp.get("/health")
def health():
    return {
        "status": "ok",
        "service": "shopapi",
    }


@health_bp.get("/ready")
def readiness():
    database_ok = True

    try:
        db.session.execute(
            db.text("SELECT 1")
        )
    except Exception:
        database_ok = False

    redis_ok = redis_ping()

    if not database_ok or not redis_ok:
        return {
            "status": "not_ready",
            "database": database_ok,
            "redis": redis_ok,
        }, 503

    return {
        "status": "ready",
        "database": True,
        "redis": True,
    }
