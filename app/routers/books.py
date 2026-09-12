from fastapi import APIRouter, status

from app.schemas.book import BookOut, BookUpdate
from app.services import book as book_service

router = APIRouter(prefix="/books", tags=["books"])


@router.patch("/{isbn}", response_model=BookOut)
async def update_book(isbn: str, data: BookUpdate):
    return await book_service.update_book(isbn, data)


@router.delete("/{isbn}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(isbn: str):
    await book_service.delete_book(isbn)
