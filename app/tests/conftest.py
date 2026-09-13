import pytest
from beanie import init_beanie
from pymongo import AsyncMongoClient

from app.core.config import settings
from app.models.book import Book
from app.models.cache_entry import CacheEntry
from app.models.cached_cover import CachedCover
from app.models.library_entry import LibraryEntry

TEST_DATABASE_NAME = "shelfie_test"


@pytest.fixture(autouse=True)
async def db():
    client = AsyncMongoClient(settings.mongodb_uri)
    await init_beanie(
        database=client[TEST_DATABASE_NAME], 
        document_models=[Book, LibraryEntry, CacheEntry, CachedCover]
    )

    yield

    await CachedCover.delete_all()
    await CacheEntry.delete_all()
    await LibraryEntry.delete_all()
    await Book.delete_all()
    await client.close()
