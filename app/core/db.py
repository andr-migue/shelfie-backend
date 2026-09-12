from pymongo import AsyncMongoClient
from beanie import init_beanie
from app.core.config import settings

async def init_db() -> AsyncMongoClient:
    client = AsyncMongoClient(settings.mongodb_uri)
    
    await init_beanie(
        database=client[settings.database_name],
        document_models=[],
    )
    
    return client