from datetime import datetime

from pydantic import BaseModel

from app.models.enums import ReadingStatus
from app.models.library_entry import Note


class LibraryEntryOut(BaseModel):
    book: int
    status: ReadingStatus
    rating: int | None = None
    notes: list[Note] = []
    started_at: datetime | None = None
    finished_at: datetime | None = None

class LibraryEntryCreate(BaseModel):
    book: int
    status: ReadingStatus = ReadingStatus.WANT_TO_READ
    rating: int | None = None
    notes: list[Note] = []
    started_at: datetime | None = None
    finished_at: datetime | None = None
    added_at: datetime

class LibraryEntryUpdate(BaseModel):
    status: ReadingStatus | None = None
    rating: int | None = None
    notes: list[Note] | None = None
    started_at: datetime | None = None
    finished_at: datetime | None = None