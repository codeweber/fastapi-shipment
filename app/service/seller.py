from datetime import UTC, datetime, timedelta
from typing import Optional
from uuid import UUID

from pwdlib import PasswordHash
from redis.asyncio import Redis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


from app.api.schema.seller import SellerWithPassword
from app.database.model import Seller
from .utils import encode_access_token

class SellerService:

    def __init__(self, session: AsyncSession, redis: Redis):
        self.session = session
        self.redis = redis
        self._password_hash = PasswordHash.recommended()

    def hash(self, password: str) -> str: 
        return self._password_hash.hash(password)
    
    def verify(self, cleartext: str, encryptedtext: str) -> bool:
        return self._password_hash.verify(cleartext, encryptedtext)

    async def create(self, details: SellerWithPassword) -> Seller:
        new_seller = Seller(
            **details.model_dump(exclude=["password"]),
            password_hash=self.hash(details.password),
        )
        self.session.add(new_seller)
        await self.session.commit()
        await self.session.refresh(new_seller)

        return new_seller

    async def token(self, username: str, password: str) -> Optional[str]:
        stmt = select(Seller).where(Seller.email == username)
        result = await self.session.scalars(stmt)
        
        maybe_seller = result.one_or_none()
        
        if not maybe_seller or not (
            self.verify(password, maybe_seller.password_hash)
        ):
            return None
        
        token = encode_access_token(data={
            "user": {
                "id": str(maybe_seller.id),
            }
        })

        return token
    
    async def get(self, id: UUID) -> Optional[Seller]:
        return (await self.session.get(Seller, id))
    
    async def blacklist_token(self, token_id: str, expiry: datetime) -> None:
        current_timestamp = datetime.now(UTC)
        if expiry <= current_timestamp:
            ttl = timedelta(days=1)
        else:
            ttl = (expiry - current_timestamp) + timedelta(days=1)
        await self.redis.set(token_id, current_timestamp.isoformat(), ttl)

    async def is_token_blacklisted(self, token_id: str) -> bool:
        result = await self.redis.get(token_id)
        if (result):
            return True
        else:
            return False