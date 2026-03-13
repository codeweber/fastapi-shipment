from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.database.session import create_tables
from .api.router import router

@asynccontextmanager
async def lifespan_handler(app: FastAPI):
    await create_tables()
    yield

app = FastAPI(lifespan=lifespan_handler)

app.include_router(router)