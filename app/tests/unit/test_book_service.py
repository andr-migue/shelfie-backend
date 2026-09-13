from datetime import UTC, datetime

import pytest

from app.core.exceptions import BookInUseError, BookNotFoundError
from app.models.book import Book
from app.models.library_entry import LibraryEntry
from app.schemas.book import BookUpdate
from app.services import book as book_service

ISBN = "0451524934"


async def make_book() -> Book:
    book = Book(
        isbn=ISBN,
        title="Nineteen Eighty-Four",
        authors=["George Orwell"],
        source="open_library",
        fetched_at=datetime.now(UTC),
    )
    await book.insert()
    return book


async def test_update_book_raises_when_not_found():
    with pytest.raises(BookNotFoundError):
        await book_service.update_book(ISBN, BookUpdate(title="Nuevo título"))


async def test_update_book_applies_only_provided_fields():
    await make_book()

    updated = await book_service.update_book(ISBN, BookUpdate(title="1984"))

    assert updated.title == "1984"
    assert updated.authors == ["George Orwell"]


async def test_delete_book_raises_when_not_found():
    with pytest.raises(BookNotFoundError):
        await book_service.delete_book(ISBN)


async def test_delete_book_raises_when_referenced_by_library_entry():
    book = await make_book()
    entry = LibraryEntry(book=book, added_at=datetime.now(UTC))
    await entry.insert()

    with pytest.raises(BookInUseError):
        await book_service.delete_book(ISBN)

    assert await Book.find(Book.isbn == ISBN).count() == 1


async def test_delete_book_removes_unreferenced_book():
    await make_book()

    await book_service.delete_book(ISBN)

    assert await Book.find_one(Book.isbn == ISBN) is None
