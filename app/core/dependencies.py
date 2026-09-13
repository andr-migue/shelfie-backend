from typing import Annotated

from fastapi import Depends, HTTPException, Query, Request

from app.core.config import settings
from app.core.protocols import BookClient
from app.integrations.open_library.client import OpenLibraryClient
from app.services.cached_book_client import CachedBookClient


def get_book_client(
    request: Request,
    provider: Annotated[str | None, Query(description="Book catalog provider to use for this request")] = None,
) -> BookClient:
    selected = provider or settings.book_provider

    if selected == "open_library":
        return CachedBookClient(OpenLibraryClient(request.app.state.open_library_http_client))

    raise HTTPException(status_code=400, detail=f"Unknown book provider: {selected}")


BookClientDep = Annotated[BookClient, Depends(get_book_client)]
