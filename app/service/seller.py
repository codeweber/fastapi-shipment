from typing import Optional
from uuid import UUID

from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession


from app.api.schema.seller import SellerWithPassword
from app.database.model import Seller
from app.service.notification import NotificationService
from app.service.user import UserService

class SellerService(UserService):

    def __init__(self, session: AsyncSession, redis: Redis, notification_service: NotificationService):
        super().__init__(user_type=Seller, session=session, redis=redis, notification_service=notification_service)

    async def create(self, details: SellerWithPassword) -> Seller:
        new_seller = Seller(
            **details.model_dump(exclude=["password"]),
            password_hash=self.hash(details.password),
        )
        seller = await self._add(new_seller)

        self.send_verification(seller)

        return seller
        
    async def get(self, id: UUID) -> Optional[Seller]:
        return (await self._get(id))
    