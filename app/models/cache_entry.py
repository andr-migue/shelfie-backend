from datetime import datetime
from typing import Annotated

from beanie import Document, Indexed
from pymongo import IndexModel


class CacheEntry(Document):
    key: Annotated[str, Indexed(unique=True)]
    value: dict
    expires_at: datetime
    
    class Settings:
        name = "cache_entries"
        indexes = [  # noqa: RUF012
            IndexModel("expires_at", expireAfterSeconds=0)
        ]