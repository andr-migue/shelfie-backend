from app.core.exceptions import BookInUseError, BookNotFoundError
from app.models.book import Book
from app.models.library_entry import LibraryEntry
from app.schemas.book import BookUpdate


async def update_book(isbn: str, data: BookUpdate) -> Book:
    book = await Book.find_one(Book.isbn == isbn)
    if book is None:
        raise BookNotFoundError(isbn)

    updates = data.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(book, field, value)

    await book.save()
    return book


async def delete_book(isbn: str) -> None:
    book = await Book.find_one(Book.isbn == isbn)
    if book is None:
        raise BookNotFoundError(isbn)
    
    library_entry = await LibraryEntry.find_one(LibraryEntry.book.id == book.id)
    if library_entry is not None:
        raise BookInUseError(isbn)
    
    await book.delete()
