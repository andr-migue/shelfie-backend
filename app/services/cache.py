from datetime import UTC, datetime, timedelta

from app.models.cache_entry import CacheEntry


async def get(key: str) -> dict | None:
    entry = await CacheEntry.find_one(CacheEntry.key == key)
    if entry is None:
        return None

    expires_at = entry.expires_at.replace(tzinfo=UTC) if entry.expires_at.tzinfo is None else entry.expires_at
    if expires_at <= datetime.now(UTC):
        return None

    return entry.value


async def set(key: str, value: dict, ttl_seconds: int) -> None:
    expires_at = datetime.now(UTC) + timedelta(seconds=ttl_seconds)
    existing = await CacheEntry.find_one(CacheEntry.key == key)

    if existing is not None:
        existing.value = value
        existing.expires_at = expires_at
        await existing.save()
        return

    await CacheEntry(key=key, value=value, expires_at=expires_at).insert()
