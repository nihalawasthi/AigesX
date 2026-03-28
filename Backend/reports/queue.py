from __future__ import annotations

import os
from typing import Optional

try:
    import redis
except Exception:  # pragma: no cover
    redis = None


QUEUE_KEY = os.getenv("AIGESX_SCAN_QUEUE_KEY", "aigesx:scan_jobs")


def _get_client():
    if redis is None:
        return None
    redis_url = os.getenv("REDIS_URL", "redis://127.0.0.1:6379/0")
    try:
        client = redis.Redis.from_url(redis_url, decode_responses=True)
        client.ping()
        return client
    except Exception:
        return None


def enqueue_scan_job(job_id: str) -> bool:
    client = _get_client()
    if not client:
        return False
    client.rpush(QUEUE_KEY, str(job_id))
    return True


def dequeue_scan_job_blocking(timeout_seconds: int = 5) -> Optional[str]:
    client = _get_client()
    if not client:
        return None
    item = client.blpop(QUEUE_KEY, timeout=max(1, timeout_seconds))
    if not item:
        return None
    _, value = item
    return value
