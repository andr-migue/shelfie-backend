from beanie import init_beanie
from pymongo import AsyncMongoClient

from app.core.config import settings
from app.models.book import Book
from app.models.library_entry import LibraryEntry


async def init_db() -> AsyncMongoClient:
    client = AsyncMongoClient(settings.mongodb_uri)

    await init_beanie(
        database=client[settings.database_name],
        document_models=[Book, LibraryEntry],
    )

    return client
