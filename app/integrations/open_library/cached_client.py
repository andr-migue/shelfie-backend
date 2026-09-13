from dataclasses import asdict

from app.core.protocols import BookMetadata
from app.integrations.open_library.client import OpenLibraryClient
from app.services import cache as cache_service

ISBN_CACHE_TTL_SECONDS = 60 * 60 * 24 * 30  # 30 days
SEARCH_CACHE_TTL_SECONDS = 60 * 15  # 15 minutes


class CachedOpenLibraryClient:
    def __init__(self, client: OpenLibraryClient) -> None:
        self._client = client

    async def get_by_isbn(self, isbn: str) -> BookMetadata | None:
        key = f"isbn:{isbn}"
        cached = await cache_service.get(key)
        if cached is not None:
            return BookMetadata(**cached["data"]) if cached["found"] else None

        result = await self._client.get_by_isbn(isbn)

        value = {"found": True, "data": asdict(result)} if result is not None else {"found": False}
        await cache_service.set(key, value, ISBN_CACHE_TTL_SECONDS)

        return result

    async def search(self, query: str) -> list[BookMetadata]:
        key = f"search:{query.strip().lower()}"
        cached = await cache_service.get(key)
        if cached is not None:
            return [BookMetadata(**item) for item in cached["results"]]

        results = await self._client.search(query)

        await cache_service.set(key, {"results": [asdict(r) for r in results]}, SEARCH_CACHE_TTL_SECONDS)

        return results
