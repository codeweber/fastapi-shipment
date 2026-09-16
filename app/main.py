from contextlib import asynccontextmanager

from fastapi import FastAPI
from scalar_fastapi import get_scalar_api_reference

from app.api.dependencies import NotificationServiceDep
from app.api.routers import delivery_partner
from app.api.schema.mail import Mail
from app.database.redis import close_redis_connection_pool, get_redis_connection_pool
from app.database.session import create_tables

from .api.routers import review, seller, shipment


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
app.include_router(delivery_partner.router)
app.include_router(review.router)

@app.post("/mail")
async def get_mail(mail: Mail, notification_service: NotificationServiceDep):

    notification_service.send_email(
        recipients=mail.recipients,
        subject=mail.subject,
        body=mail.body
    )

    return mail.model_dump()

@app.get("/scalar", include_in_schema=False)
async def get_scalar_docs():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title="Scalar API",
    )