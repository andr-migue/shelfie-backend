import httpx
import pytest

from app.core.exceptions import (
    BookNotFoundInCatalogError,
    DuplicateLibraryEntryError,
    LibraryEntryNotFoundError,
)
from app.core.protocols import BookMetadata
from app.models.book import Book
from app.models.enums import ReadingStatus
from app.schemas.library_entry import LibraryEntryUpdate
from app.services import library as library_service

ISBN = "0451524934"

BOOK_RESULT = BookMetadata(
    title="Nineteen Eighty-Four",
    authors=["George Orwell"],
    isbn=ISBN,
    cover_url="https://covers.openlibrary.org/b/id/12054527-M.jpg",
    publisher="Signet Classics",
    published_year=1993,
    page_count=328,
)


class FakeBookClient:
    def __init__(self, result: BookMetadata | None = None, error: Exception | None = None) -> None:
        self._result = result
        self._error = error
        self.calls = 0

    async def get_by_isbn(self, isbn: str) -> BookMetadata | None:
        self.calls += 1
        if self._error is not None:
            raise self._error
        return self._result


async def test_get_or_create_book_creates_new_book():
    client = FakeBookClient(result=BOOK_RESULT)

    book = await library_service.get_or_create_book(client, ISBN)

    assert book.isbn == ISBN
    assert book.title == "Nineteen Eighty-Four"
    assert book.source == "open_library"
    assert await Book.find(Book.isbn == ISBN).count() == 1


async def test_get_or_create_book_reuses_existing_without_calling_open_library():
    client = FakeBookClient(result=BOOK_RESULT)

    first = await library_service.get_or_create_book(client, ISBN)
    second = await library_service.get_or_create_book(client, ISBN)

    assert first.id == second.id
    assert client.calls == 1


async def test_get_or_create_book_raises_when_isbn_not_found():
    client = FakeBookClient(result=None)

    with pytest.raises(BookNotFoundInCatalogError):
        await library_service.get_or_create_book(client, ISBN)


async def test_get_or_create_book_propagates_timeout_when_open_library_is_down():
    client = FakeBookClient(error=httpx.TimeoutException("timed out"))

    with pytest.raises(httpx.TimeoutException):
        await library_service.get_or_create_book(client, ISBN)


async def test_create_library_entry_raises_on_duplicate():
    client = FakeBookClient(result=BOOK_RESULT)

    await library_service.create_library_entry(client, ISBN)

    with pytest.raises(DuplicateLibraryEntryError):
        await library_service.create_library_entry(client, ISBN)


async def test_update_entry_raises_when_not_found():
    with pytest.raises(LibraryEntryNotFoundError):
        await library_service.update_entry("000000000000000000000000", LibraryEntryUpdate())


async def test_update_entry_raises_on_malformed_id():
    with pytest.raises(LibraryEntryNotFoundError):
        await library_service.update_entry("not-an-object-id", LibraryEntryUpdate())


async def test_update_entry_applies_only_provided_fields():
    client = FakeBookClient(result=BOOK_RESULT)
    entry = await library_service.create_library_entry(client, ISBN)

    updated = await library_service.update_entry(
        str(entry.id), LibraryEntryUpdate(status=ReadingStatus.FINISHED)
    )

    assert updated.status == ReadingStatus.FINISHED
    assert updated.rating is None


async def test_delete_entry_removes_it_but_keeps_the_book():
    client = FakeBookClient(result=BOOK_RESULT)
    entry = await library_service.create_library_entry(client, ISBN)

    await library_service.delete_entry(str(entry.id))

    with pytest.raises(LibraryEntryNotFoundError):
        await library_service.get_entry(str(entry.id))
    assert await Book.find(Book.isbn == ISBN).count() == 1


async def test_list_entries_filters_by_status():
    client = FakeBookClient(result=BOOK_RESULT)
    entry = await library_service.create_library_entry(client, ISBN)
    await library_service.update_entry(str(entry.id), LibraryEntryUpdate(status=ReadingStatus.READING))

    reading = await library_service.list_entries(status=ReadingStatus.READING)
    finished = await library_service.list_entries(status=ReadingStatus.FINISHED)

    assert len(reading) == 1
    assert len(finished) == 0


async def test_list_entries_filters_by_search_on_title_or_author():
    client = FakeBookClient(result=BOOK_RESULT)
    await library_service.create_library_entry(client, ISBN)

    by_author = await library_service.list_entries(search="orwell")
    no_match = await library_service.list_entries(search="tolkien")

    assert len(by_author) == 1
    assert len(no_match) == 0


async def test_add_note_appends_to_existing_notes():
    client = FakeBookClient(result=BOOK_RESULT)
    entry = await library_service.create_library_entry(client, ISBN)

    updated = await library_service.add_note(str(entry.id), "Excelente distopia")

    assert len(updated.notes) == 1
    assert updated.notes[0].text == "Excelente distopia"
