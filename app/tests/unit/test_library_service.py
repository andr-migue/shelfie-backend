import httpx
import pytest

from app.core.exceptions import (
    BookNotFoundInOpenLibraryError,
    DuplicateLibraryEntryError,
    LibraryEntryNotFoundError,
)
from app.integrations.open_library.client import OpenLibraryClient
from app.models.book import Book
from app.models.enums import ReadingStatus
from app.schemas.library_entry import LibraryEntryUpdate
from app.services import library as library_service

ISBN = "0451524934"

OPEN_LIBRARY_RESPONSE = {
    f"ISBN:{ISBN}": {
        "title": "Nineteen Eighty-Four",
        "authors": [{"name": "George Orwell"}],
        "publishers": [{"name": "Signet Classics"}],
        "publish_date": "1993",
        "number_of_pages": 328,
        "cover": {"medium": "https://covers.openlibrary.org/b/id/12054527-M.jpg"},
    }
}


def make_client() -> OpenLibraryClient:
    http_client = httpx.AsyncClient(base_url="https://openlibrary.org", timeout=5.0)
    return OpenLibraryClient(http_client)


async def test_get_or_create_book_creates_new_book(respx_mock):
    respx_mock.get("https://openlibrary.org/api/books").mock(
        return_value=httpx.Response(200, json=OPEN_LIBRARY_RESPONSE)
    )
    client = make_client()

    book = await library_service.get_or_create_book(client, ISBN)

    assert book.isbn == ISBN
    assert book.title == "Nineteen Eighty-Four"
    assert book.source == "open_library"
    assert await Book.find(Book.isbn == ISBN).count() == 1


async def test_get_or_create_book_reuses_existing_without_calling_open_library(respx_mock):
    route = respx_mock.get("https://openlibrary.org/api/books").mock(
        return_value=httpx.Response(200, json=OPEN_LIBRARY_RESPONSE)
    )
    client = make_client()

    first = await library_service.get_or_create_book(client, ISBN)
    second = await library_service.get_or_create_book(client, ISBN)

    assert first.id == second.id
    assert route.call_count == 1


async def test_get_or_create_book_raises_when_isbn_not_found(respx_mock):
    respx_mock.get("https://openlibrary.org/api/books").mock(
        return_value=httpx.Response(200, json={})
    )
    client = make_client()

    with pytest.raises(BookNotFoundInOpenLibraryError):
        await library_service.get_or_create_book(client, ISBN)


async def test_get_or_create_book_propagates_timeout_when_open_library_is_down(respx_mock):
    respx_mock.get("https://openlibrary.org/api/books").mock(
        side_effect=httpx.TimeoutException("timed out")
    )
    client = make_client()

    with pytest.raises(httpx.TimeoutException):
        await library_service.get_or_create_book(client, ISBN)


async def test_create_library_entry_raises_on_duplicate(respx_mock):
    respx_mock.get("https://openlibrary.org/api/books").mock(
        return_value=httpx.Response(200, json=OPEN_LIBRARY_RESPONSE)
    )
    client = make_client()

    await library_service.create_library_entry(client, ISBN)

    with pytest.raises(DuplicateLibraryEntryError):
        await library_service.create_library_entry(client, ISBN)


async def test_update_entry_raises_when_not_found():
    with pytest.raises(LibraryEntryNotFoundError):
        await library_service.update_entry("000000000000000000000000", LibraryEntryUpdate())


async def test_update_entry_raises_on_malformed_id():
    with pytest.raises(LibraryEntryNotFoundError):
        await library_service.update_entry("not-an-object-id", LibraryEntryUpdate())


async def test_update_entry_applies_only_provided_fields(respx_mock):
    respx_mock.get("https://openlibrary.org/api/books").mock(
        return_value=httpx.Response(200, json=OPEN_LIBRARY_RESPONSE)
    )
    client = make_client()
    entry = await library_service.create_library_entry(client, ISBN)

    updated = await library_service.update_entry(
        str(entry.id), LibraryEntryUpdate(status=ReadingStatus.FINISHED)
    )

    assert updated.status == ReadingStatus.FINISHED
    assert updated.rating is None


async def test_delete_entry_removes_it_but_keeps_the_book(respx_mock):
    respx_mock.get("https://openlibrary.org/api/books").mock(
        return_value=httpx.Response(200, json=OPEN_LIBRARY_RESPONSE)
    )
    client = make_client()
    entry = await library_service.create_library_entry(client, ISBN)

    await library_service.delete_entry(str(entry.id))

    with pytest.raises(LibraryEntryNotFoundError):
        await library_service.get_entry(str(entry.id))
    assert await Book.find(Book.isbn == ISBN).count() == 1


async def test_list_entries_filters_by_status(respx_mock):
    respx_mock.get("https://openlibrary.org/api/books").mock(
        return_value=httpx.Response(200, json=OPEN_LIBRARY_RESPONSE)
    )
    client = make_client()
    entry = await library_service.create_library_entry(client, ISBN)
    await library_service.update_entry(str(entry.id), LibraryEntryUpdate(status=ReadingStatus.READING))

    reading = await library_service.list_entries(status=ReadingStatus.READING)
    finished = await library_service.list_entries(status=ReadingStatus.FINISHED)

    assert len(reading) == 1
    assert len(finished) == 0


async def test_list_entries_filters_by_search_on_title_or_author(respx_mock):
    respx_mock.get("https://openlibrary.org/api/books").mock(
        return_value=httpx.Response(200, json=OPEN_LIBRARY_RESPONSE)
    )
    client = make_client()
    await library_service.create_library_entry(client, ISBN)

    by_author = await library_service.list_entries(search="orwell")
    no_match = await library_service.list_entries(search="tolkien")

    assert len(by_author) == 1
    assert len(no_match) == 0


async def test_add_note_appends_to_existing_notes(respx_mock):
    respx_mock.get("https://openlibrary.org/api/books").mock(
        return_value=httpx.Response(200, json=OPEN_LIBRARY_RESPONSE)
    )
    client = make_client()
    entry = await library_service.create_library_entry(client, ISBN)

    updated = await library_service.add_note(str(entry.id), "Excelente distopia")

    assert len(updated.notes) == 1
    assert updated.notes[0].text == "Excelente distopia"
