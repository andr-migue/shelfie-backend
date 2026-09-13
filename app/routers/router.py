from fastapi import APIRouter

from app.routers import books, catalog

router = APIRouter()

router.include_router(books.router)
router.include_router(catalog.router)
