from fastapi import APIRouter, status

from app.integrations.open_library.dependencies import OpenLibraryClientDep
from app.models.library_entry import LibraryEntry
from app.schemas.library_entry import (
    LibraryEntryCreate,
    LibraryEntryOut,
    LibraryEntryUpdate,
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
async def add_to_library(data: LibraryEntryCreate, client: OpenLibraryClientDep):
    entry = await library_service.create_library_entry(client, data.isbn)
    return _to_out(entry)


@router.patch("/{entry_id}", response_model=LibraryEntryOut)
async def update_library_entry(entry_id: str, data: LibraryEntryUpdate):
    entry = await library_service.update_entry(entry_id, data)
    return _to_out(entry)


@router.delete("/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_library_entry(entry_id: str) -> None:
    await library_service.delete_entry(entry_id)
