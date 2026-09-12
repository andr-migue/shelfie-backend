from datetime import datetime

from beanie import Document, Link
from pydantic import BaseModel, Field

from app.models.book import Book
from app.models.enums import ReadingStatus


class Note(BaseModel):
    text: str
    created_at: datetime


class LibraryEntry(Document):
    book: Link[Book]
    status: ReadingStatus = ReadingStatus.WANT_TO_READ
    rating: int | None = None
    notes: list[Note] = Field(default_factory=list)
    started_at: datetime | None = None
    finished_at: datetime | None = None
    added_at: datetime
