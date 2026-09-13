from fastapi import APIRouter, Request
from fastapi.responses import Response

from app.core.dependencies import BookClientDep
from app.integrations.open_library.mapper import from_book_result
from app.schemas.book import BookOut
from app.services import cover_cache as cover_cache_service

router = APIRouter(prefix="/catalog", tags=["catalog"])


@router.get("/search", response_model=list[BookOut])
async def search(query: str, client: BookClientDep):
    results = await client.search(query)
    return [from_book_result(book) for book in results]


@router.get("/covers")
async def get_cover(src: str, request: Request):
    data, content_type = await cover_cache_service.get_cover(src, request.app.state.open_library_http_client)
    return Response(
        content=data,
        media_type=content_type,
        headers={"Cache-Control": "public, max-age=31536000, immutable"},
    )


@router.get("/{isbn}", response_model=BookOut)
async def get_by_isbn(isbn: str, client: BookClientDep):
    book = await client.get_by_isbn(isbn)
    return from_book_result(book)
