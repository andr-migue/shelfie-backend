from app.services import cache as cache_service


async def test_get_returns_none_when_key_does_not_exist():
    assert await cache_service.get("missing") is None


async def test_set_then_get_returns_the_same_value():
    await cache_service.set("key", {"a": 1}, ttl_seconds=60)

    assert await cache_service.get("key") == {"a": 1}


async def test_set_overwrites_existing_value_for_the_same_key():
    await cache_service.set("key", {"a": 1}, ttl_seconds=60)
    await cache_service.set("key", {"a": 2}, ttl_seconds=60)

    assert await cache_service.get("key") == {"a": 2}


async def test_get_returns_none_when_entry_is_expired():
    await cache_service.set("key", {"a": 1}, ttl_seconds=-1)

    assert await cache_service.get("key") is None
