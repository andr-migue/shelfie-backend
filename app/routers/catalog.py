from fastapi import APIRouter

from app.integrations.open_library.dependencies import OpenLibraryClientDep
from app.integrations.open_library.mapper import from_book_result, from_search_result
from app.schemas.book import BookOut

router = APIRouter(prefix="/catalog", tags=["catalog"])


@router.get("/search", response_model=list[BookOut])
async def search(query: str, client: OpenLibraryClientDep):
    search_results = await client.search(query)
    return [
        from_search_result(book) for book in search_results if book.isbn is not None
    ]


@router.get("/{isbn}", response_model=BookOut)
async def get_by_isbn(isbn: str, client: OpenLibraryClientDep):
    book = await client.get_by_isbn(isbn)
    return from_book_result(book)
