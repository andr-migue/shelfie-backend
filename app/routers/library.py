from fastapi import APIRouter, status

from app.core.dependencies import BookClientDep
from app.models.enums import ReadingStatus
from app.models.library_entry import LibraryEntry
from app.schemas.library_entry import (
    LibraryEntryCreate,
    LibraryEntryOut,
    LibraryEntryUpdate,
    NoteCreate,
)
from app.services import library as library_service

router = APIRouter(prefix="/library", tags=["library"])


def _to_out(entry: LibraryEntry) -> LibraryEntryOut:
    return LibraryEntryOut.model_validate(
        {
            "id": str(entry.id),
            "book": entry.book,
            "status": entry.status,
            "rating": entry.rating,
            "notes": entry.notes,
            "started_at": entry.started_at,
            "finished_at": entry.finished_at,
            "added_at": entry.added_at,
        },
        from_attributes=True,
    )


@router.post("", response_model=LibraryEntryOut, status_code=status.HTTP_201_CREATED)
async def add_to_library(data: LibraryEntryCreate, client: BookClientDep):
    entry = await library_service.create_library_entry(client, data.isbn)
    return _to_out(entry)


@router.get("", response_model=list[LibraryEntryOut])
async def list_library(status: ReadingStatus | None = None, search: str | None = None):
    entries = await library_service.list_entries(status=status, search=search)
    return [_to_out(entry) for entry in entries]


@router.get("/{entry_id}", response_model=LibraryEntryOut)
async def get_library_entry(entry_id: str):
    entry = await library_service.get_entry(entry_id)
    return _to_out(entry)


@router.patch("/{entry_id}", response_model=LibraryEntryOut)
async def update_library_entry(entry_id: str, data: LibraryEntryUpdate):
    entry = await library_service.update_entry(entry_id, data)
    return _to_out(entry)


@router.delete("/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_library_entry(entry_id: str) -> None:
    await library_service.delete_entry(entry_id)


@router.post("/{entry_id}/notes", response_model=LibraryEntryOut, status_code=status.HTTP_201_CREATED)
async def add_note_to_entry(entry_id: str, data: NoteCreate):
    entry = await library_service.add_note(entry_id, data.text)
    return _to_out(entry)
