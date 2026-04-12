from datetime import UTC, datetime, timedelta
from typing import Optional

from pwdlib import PasswordHash
from redis.asyncio import Redis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.model import UserMixin
from app.service.utils import encode_access_token


class UserService:
    
    def __init__(self, user_type: UserMixin, session: AsyncSession, redis: Redis):
        self.user_type = user_type
        self.session = session
        self.redis = redis
        self._password_hash = PasswordHash.recommended()

    def hash(self, password: str) -> str: 
        return self._password_hash.hash(password)
    
    def verify(self, cleartext: str, encryptedtext: str) -> bool:
        return self._password_hash.verify(cleartext, encryptedtext)
    
    async def token(self, username: str, password: str) -> Optional[str]:
        stmt = select(self.user_type).where(self.user_type.email == username)
        result = await self.session.scalars(stmt)
        
        maybe_user = result.one_or_none()
        
        if not maybe_user or not (
            self.verify(password, maybe_user.password_hash)
        ):
            return None
        
        token = encode_access_token(data={
            "user": {
                "id": str(maybe_user.id),
            }
        })

        return token
    
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