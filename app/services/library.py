from datetime import UTC, datetime

from app.core.exceptions import (
    BookNotFoundInOpenLibraryError,
    DuplicateLibraryEntryError,
)
from app.integrations.open_library.client import OpenLibraryClient
from app.integrations.open_library.mapper import from_book_result_to_book_create
from app.models.book import Book
from app.models.library_entry import LibraryEntry


async def get_or_create_book(client: OpenLibraryClient, isbn: str) -> Book:
    existing = await Book.find_one(Book.isbn == isbn)
    if existing is not None:
        return existing

    result = await client.get_by_isbn(isbn)
    if result is None:
        raise BookNotFoundInOpenLibraryError(isbn)

    book_create = from_book_result_to_book_create(result)
    book = Book(**book_create.model_dump())
    await book.insert()
    return book


async def create_library_entry(client: OpenLibraryClient, isbn: str) -> LibraryEntry:
    book = await get_or_create_book(client, isbn)

    existing_entry = await LibraryEntry.find_one(LibraryEntry.book.id == book.id)
    if existing_entry is not None:
        raise DuplicateLibraryEntryError(isbn)

    entry = LibraryEntry(book=book, added_at=datetime.now(UTC))
    await entry.insert()
    return entry
