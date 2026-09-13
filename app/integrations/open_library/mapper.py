from datetime import UTC, datetime

from app.core.protocols import BookMetadata
from app.schemas.book import BookCreate, BookOut


def from_book_result(result: BookMetadata) -> BookOut:
    return BookOut(
        isbn=result.isbn,
        title=result.title,
        authors=result.authors,
        cover_url=result.cover_url,
        publisher=result.publisher,
        published_year=result.published_year,
        page_count=result.page_count,
    )


def from_book_result_to_book_create(result: BookMetadata) -> BookCreate:
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
