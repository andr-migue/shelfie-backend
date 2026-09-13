from typing import Annotated

from fastapi import Depends, Request

from app.core.protocols import BookClient
from app.integrations.open_library.client import OpenLibraryClient
from app.services.cached_book_client import CachedBookClient


def get_book_client(request: Request) -> BookClient:
    return CachedBookClient(OpenLibraryClient(request.app.state.open_library_http_client))


BookClientDep = Annotated[BookClient, Depends(get_book_client)]
