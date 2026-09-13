from fastapi import APIRouter

from app.routers import books, catalog

api_router = APIRouter()

api_router.include_router(books.router)
api_router.include_router(catalog.router)
