import re
from urllib.parse import quote

import httpx

from app.core.config import settings
from app.core.protocols import BookMetadata

SEARCH_FIELDS = "title,author_name,isbn,cover_i,publisher,first_publish_year,number_of_pages_median"

class OpenLibraryClient:
    def __init__(self, http_client: httpx.AsyncClient) -> None:
        self._http_client = http_client

    async def search(self, query: str) -> list[BookMetadata]:
        response = await self._http_client.get(
            "/search.json",
            params={"q": query, "fields": SEARCH_FIELDS, "limit": 20},
        )
        response.raise_for_status()

        docs = response.json()["docs"]
        return [self._parse_search_doc(doc) for doc in docs if doc.get("isbn")]

    async def get_by_isbn(self, isbn: str) -> BookMetadata | None:
        response = await self._http_client.get(
            "/api/books",
            params={"bibkeys": f"ISBN:{isbn}", "jscmd": "data", "format": "json"},
        )
        response.raise_for_status()

        book = response.json().get(f"ISBN:{isbn}")
        if book is None:
            return None

        return self._parse_book(isbn, book)

    def _parse_search_doc(self, doc: dict) -> BookMetadata:
        publishers = doc.get("publisher") or []
        cover_id = doc.get("cover_i")
        cover_url = (
            self._proxy_cover_url(f"https://covers.openlibrary.org/b/id/{cover_id}-M.jpg")
            if cover_id is not None
            else None
        )

        return BookMetadata(
            title=doc.get("title", ""),
            authors=doc.get("author_name") or [],
            isbn=doc["isbn"][0],
            cover_url=cover_url,
            publisher=publishers[0] if publishers else None,
            published_year=doc.get("first_publish_year"),
            page_count=doc.get("number_of_pages_median"),
        )

    def _parse_book(self, isbn: str, book: dict) -> BookMetadata:
        publishers = book.get("publishers") or []
        cover = book.get("cover") or {}
        source_cover_url = cover.get("medium")
        cover_url = self._proxy_cover_url(source_cover_url) if source_cover_url is not None else None

        return BookMetadata(
            title=book.get("title", ""),
            authors=[author["name"] for author in book.get("authors", [])],
            isbn=isbn,
            cover_url=cover_url,
            publisher=publishers[0]["name"] if publishers else None,
            published_year=self._extract_year(book.get("publish_date")),
            page_count=book.get("number_of_pages"),
        )

    @staticmethod
    def _extract_year(publish_date: str | None) -> int | None:
        if not publish_date:
            return None
        match = re.search(r"\d{4}", publish_date)
        return int(match.group()) if match else None

    @staticmethod
    def _proxy_cover_url(source_url: str) -> str:
        return f"{settings.public_base_url}/catalog/covers?src={quote(source_url, safe='')}"
