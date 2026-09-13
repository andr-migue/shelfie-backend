from fastapi import APIRouter

from app.core.dependencies import BookClientDep
from app.integrations.open_library.mapper import from_book_result
from app.schemas.book import BookOut

router = APIRouter(prefix="/catalog", tags=["catalog"])


@router.get("/search", response_model=list[BookOut])
async def search(query: str, client: BookClientDep):
    results = await client.search(query)
    return [from_book_result(book) for book in results]


@router.get("/{isbn}", response_model=BookOut)
async def get_by_isbn(isbn: str, client: BookClientDep):
    book = await client.get_by_isbn(isbn)
    return from_book_result(book)
