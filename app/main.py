from fastapi import FastAPI
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app):
    yield

app = FastAPI(lifespan=lifespan)