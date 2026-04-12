from typing import Optional
from uuid import UUID

from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession


from app.api.schema.seller import SellerWithPassword
from app.database.model import Seller
from app.service.user import UserService

class SellerService(UserService):

    def __init__(self, session: AsyncSession, redis: Redis):
        super().__init__(user_type=Seller, session=session, redis=redis)

    async def create(self, details: SellerWithPassword) -> Seller:
        new_seller = Seller(
            **details.model_dump(exclude=["password"]),
            password_hash=self.hash(details.password),
        )
        self.session.add(new_seller)
        await self.session.commit()
        await self.session.refresh(new_seller)

        return new_seller
    
    async def get(self, id: UUID) -> Optional[Seller]:
        return (await self.session.get(Seller, id))
    