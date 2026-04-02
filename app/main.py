from fastapi import FastAPI
from scalar_fastapi import get_scalar_api_reference
from contextlib import asynccontextmanager

from app.database.redis import close_redis_connection_pool, get_redis_connection_pool
from app.database.session import create_tables
from .api.routers import shipment, seller

@asynccontextmanager
async def lifespan_handler(app: FastAPI):
    await create_tables()
    app.state.redis_pool = get_redis_connection_pool()
    try:
        yield
    finally:
        await close_redis_connection_pool(app.state.redis_pool)

app = FastAPI(lifespan=lifespan_handler)

app.include_router(shipment.router)
app.include_router(seller.router)

@app.get("/scalar", include_in_schema=False)
def get_scalar_docs():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title="Scalar API",
    )