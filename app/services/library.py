from datetime import UTC, datetime

from beanie.operators import In, Or, RegEx
from pydantic import ValidationError

from app.core.exceptions import (
    BookNotFoundInCatalogError,
    DuplicateLibraryEntryError,
    LibraryEntryNotFoundError,
)
from app.core.protocols import BookClient
from app.integrations.open_library.mapper import from_book_result_to_book_create
from app.models.book import Book
from app.models.enums import ReadingStatus
from app.models.library_entry import LibraryEntry, Note
from app.schemas.library_entry import LibraryEntryUpdate


async def get_or_create_book(client: BookClient, isbn: str) -> Book:
    existing = await Book.find_one(Book.isbn == isbn)
    if existing is not None:
        return existing

    result = await client.get_by_isbn(isbn)
    if result is None:
        raise BookNotFoundInCatalogError(isbn)

    book_create = from_book_result_to_book_create(result)
    book = Book(**book_create.model_dump())
    await book.insert()
    return book


async def create_library_entry(client: BookClient, isbn: str) -> LibraryEntry:
    book = await get_or_create_book(client, isbn)

    existing_entry = await LibraryEntry.find_one(LibraryEntry.book.id == book.id)
    if existing_entry is not None:
        raise DuplicateLibraryEntryError(isbn)

    entry = LibraryEntry(book=book, added_at=datetime.now(UTC))
    await entry.insert()
    return entry


async def get_entry(entry_id: str) -> LibraryEntry:
    try:
        entry = await LibraryEntry.get(entry_id, fetch_links=True)
    except ValidationError as exc:
        raise LibraryEntryNotFoundError(entry_id) from exc

    if entry is None:
        raise LibraryEntryNotFoundError(entry_id)

    return entry


async def list_entries(
    status: ReadingStatus | None = None, search: str | None = None
) -> list[LibraryEntry]:
    conditions = []

    if status is not None:
        conditions.append(LibraryEntry.status == status)

    if search is not None:
        matching_books = await Book.find(
            Or(RegEx(Book.title, search, "i"), RegEx(Book.authors, search, "i"))
        ).to_list()
        if not matching_books:
            return []
        conditions.append(In(LibraryEntry.book.id, [book.id for book in matching_books]))

    return await LibraryEntry.find(*conditions, fetch_links=True).to_list()


async def update_entry(entry_id: str, data: LibraryEntryUpdate) -> LibraryEntry:
    entry = await get_entry(entry_id)

    updates = data.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(entry, field, value)

    await entry.save()
    return entry


async def delete_entry(entry_id: str) -> None:
    entry = await get_entry(entry_id)
    await entry.delete()


async def add_note(entry_id: str, text: str) -> LibraryEntry:
    entry = await get_entry(entry_id)
    entry.notes.append(Note(text=text, created_at=datetime.now(UTC)))
    await entry.save()
    return entry
