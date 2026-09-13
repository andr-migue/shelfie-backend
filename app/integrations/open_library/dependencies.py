from typing import Annotated

from fastapi import Depends, Request

from app.integrations.open_library.cached_client import CachedOpenLibraryClient
from app.integrations.open_library.client import OpenLibraryClient


def get_open_library_client(request: Request) -> CachedOpenLibraryClient:
    return CachedOpenLibraryClient(OpenLibraryClient(request.app.state.open_library_http_client))


OpenLibraryClientDep = Annotated[CachedOpenLibraryClient, Depends(get_open_library_client)]
