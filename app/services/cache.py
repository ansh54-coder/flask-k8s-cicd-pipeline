import json

import redis
from flask import current_app


def get_client():
    return redis.from_url(
        current_app.config["REDIS_URL"],
        decode_responses=True,
    )


def get(key):
    try:
        value = get_client().get(key)

        if value is None:
            return None

        return json.loads(value)

    except redis.RedisError:
        current_app.logger.exception(
            "Redis GET failed for key=%s",
            key,
        )
        return None


def set(key, value, timeout=None):
    try:
        timeout = timeout or current_app.config[
            "CACHE_DEFAULT_TIMEOUT"
        ]

        get_client().setex(
            key,
            timeout,
            json.dumps(value),
        )

    except redis.RedisError:
        current_app.logger.exception(
            "Redis SET failed for key=%s",
            key,
        )


def delete(key):
    try:
        get_client().delete(key)

    except redis.RedisError:
        current_app.logger.exception(
            "Redis DELETE failed for key=%s",
            key,
        )


def ping():
    try:
        return bool(get_client().ping())
    except redis.RedisError:
        return False
