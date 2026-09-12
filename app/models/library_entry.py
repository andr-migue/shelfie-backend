from datetime import datetime
from typing import Annotated

from beanie import Document, Indexed, Link
from pydantic import BaseModel

from app.models.book import Book
from app.models.enums import ReadingStatus


class Note(BaseModel):
    text: str
    created_at: datetime


class LibraryEntry(Document):
    book: Annotated[Link[Book], Indexed(unique=True)]
    status: ReadingStatus = ReadingStatus.WANT_TO_READ
    rating: int | None = None
    notes: list[Note] = []  # noqa: RUF012
    started_at: datetime | None = None
    finished_at: datetime | None = None
    added_at: datetime

    class Settings:
        name = "library_entries"
