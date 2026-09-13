from datetime import UTC, datetime

import httpx

from app.core.exceptions import CoverHostNotAllowedError, CoverNotFoundError
from app.models.cached_cover import CachedCover

ALLOWED_COVER_HOSTS = {"covers.openlibrary.org"}


async def get_cover(source_url: str, http_client: httpx.AsyncClient) -> tuple[bytes, str]:
    if httpx.URL(source_url).host not in ALLOWED_COVER_HOSTS:
        raise CoverHostNotAllowedError(source_url)

    cached = await CachedCover.find_one(CachedCover.source_url == source_url)
    if cached is not None:
        return cached.data, cached.content_type

    response = await http_client.get(source_url)
    if response.status_code == 404:
        raise CoverNotFoundError(source_url)
    response.raise_for_status()

    content_type = response.headers.get("content-type", "image/jpeg")
    await CachedCover(
        source_url=source_url,
        content_type=content_type,
        data=response.content,
        fetched_at=datetime.now(UTC),
    ).insert()

    return response.content, content_type
