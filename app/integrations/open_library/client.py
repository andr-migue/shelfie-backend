import re

import httpx

from app.integrations.open_library.dto import (
    OpenLibraryBookResult,
    OpenLibrarySearchResult,
)

SEARCH_FIELDS = "title,author_name,isbn,cover_i,publisher,first_publish_year,number_of_pages_median"

class OpenLibraryClient:
    def __init__(self, http_client: httpx.AsyncClient) -> None:
        self._http_client = http_client

    async def search(self, query: str) -> list[OpenLibrarySearchResult]:
        response = await self._http_client.get(
            "/search.json",
            params={"q": query, "fields": SEARCH_FIELDS, "limit": 20},
        )
        response.raise_for_status()

        docs = response.json()["docs"]
        return [self._parse_search_doc(doc) for doc in docs]

    async def get_by_isbn(self, isbn: str) -> OpenLibraryBookResult | None:
        response = await self._http_client.get(
            "/api/books",
            params={"bibkeys": f"ISBN:{isbn}", "jscmd": "data", "format": "json"},
        )
        response.raise_for_status()

        book = response.json().get(f"ISBN:{isbn}")
        if book is None:
            return None

        return self._parse_book(isbn, book)

    def _parse_search_doc(self, doc: dict) -> OpenLibrarySearchResult:
        isbns = doc.get("isbn") or []
        publishers = doc.get("publisher") or []

        return OpenLibrarySearchResult(
            title=doc.get("title", ""),
            authors=doc.get("author_name") or [],
            isbn=isbns[0] if isbns else None,
            cover_id=doc.get("cover_i"),
            publisher=publishers[0] if publishers else None,
            published_year=doc.get("first_publish_year"),
            page_count=doc.get("number_of_pages_median"),
        )

    def _parse_book(self, isbn: str, book: dict) -> OpenLibraryBookResult:
        publishers = book.get("publishers") or []
        cover = book.get("cover") or {}

        return OpenLibraryBookResult(
            title=book.get("title", ""),
            authors=[author["name"] for author in book.get("authors", [])],
            isbn=isbn,
            cover_url=cover.get("medium"),
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
