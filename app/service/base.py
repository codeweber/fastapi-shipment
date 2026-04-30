
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.database.model import Base

class BaseService:

    def __init__(self, model: Base, session: AsyncSession):
        self.session = session
        self.model = model

    async def _add(self, item: Base) -> Base:
        self.session.add(item)
        await self.session.commit()
        await self.session.refresh(item)
        return item
    
    async def _get(self, id) -> Optional[Base]:
        return (await self.session.get(self.model, id))