from datetime import datetime

from pydantic import BaseModel

from app.models.enums import ReadingStatus
from app.schemas.book import BookOut


class NoteOut(BaseModel):
    text: str
    created_at: datetime


class NoteCreate(BaseModel):
    text: str


class LibraryEntryCreate(BaseModel):
    isbn: str


class LibraryEntryOut(BaseModel):
    id: str
    book: BookOut
    status: ReadingStatus
    rating: int | None = None
    notes: list[NoteOut] = []
    started_at: datetime | None = None
    finished_at: datetime | None = None
    added_at: datetime


class LibraryEntryUpdate(BaseModel):
    status: ReadingStatus | None = None
    rating: int | None = None
    started_at: datetime | None = None
    finished_at: datetime | None = None
