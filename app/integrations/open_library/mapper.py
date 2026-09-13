from datetime import UTC, datetime

from app.integrations.open_library.dto import (
    OpenLibraryBookResult,
    OpenLibrarySearchResult,
)
from app.schemas.book import BookCreate, BookOut


def from_search_result(result: OpenLibrarySearchResult) -> BookOut:
    cover_url = (
        f"https://covers.openlibrary.org/b/id/{result.cover_id}-M.jpg"
        if result.cover_id is not None
        else None
    )

    return BookOut(
        isbn=result.isbn,
        title=result.title,
        authors=result.authors,
        cover_url=cover_url,
        publisher=result.publisher,
        published_year=result.published_year,
        page_count=result.page_count,
    )


def from_book_result(result: OpenLibraryBookResult) -> BookOut:
    return BookOut(
        isbn=result.isbn,
        title=result.title,
        authors=result.authors,
        cover_url=result.cover_url,
        publisher=result.publisher,
        published_year=result.published_year,
        page_count=result.page_count,
    )


def from_book_result_to_book_create(result: OpenLibraryBookResult) -> BookCreate:
    return BookCreate(
        isbn=result.isbn,
        title=result.title,
        authors=result.authors,
        cover_url=result.cover_url,
        publisher=result.publisher,
        published_year=result.published_year,
        page_count=result.page_count,
        source="open_library",
        fetched_at=datetime.now(UTC),
    )
