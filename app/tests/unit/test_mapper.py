from datetime import UTC, datetime

from app.core.protocols import BookMetadata
from app.integrations.open_library.mapper import (
    from_book_result,
    from_book_result_to_book_create,
)


def test_from_book_result_passes_cover_url_through_unchanged():
    result = BookMetadata(
        title="Nineteen Eighty-Four",
        authors=["George Orwell"],
        isbn="0451524934",
        cover_url="https://covers.openlibrary.org/b/id/12054527-M.jpg",
        publisher="Signet Classics",
        published_year=1993,
        page_count=328,
    )

    book_out = from_book_result(result)

    assert book_out.cover_url == "https://covers.openlibrary.org/b/id/12054527-M.jpg"


def test_from_book_result_to_book_create_sets_source_and_fetched_at():
    result = BookMetadata(
        title="Nineteen Eighty-Four",
        authors=["George Orwell"],
        isbn="0451524934",
        cover_url=None,
        publisher="Signet Classics",
        published_year=1993,
        page_count=328,
    )

    before = datetime.now(UTC)
    book_create = from_book_result_to_book_create(result)
    after = datetime.now(UTC)

    assert book_create.source == "open_library"
    assert before <= book_create.fetched_at <= after
