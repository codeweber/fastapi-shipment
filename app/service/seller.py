import bcrypt
from sqlalchemy.ext.asyncio import AsyncSession


from app.api.schema.seller import SellerWithPassword
from app.database.model import Seller


class SellerService:
    
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, details: SellerWithPassword) -> Seller:
        new_seller = Seller(
            **details.model_dump(exclude=["password"]),
            password_hash = bcrypt.hashpw(
                details.password.encode("utf-8"), bcrypt.gensalt()
            ).decode(encoding="ascii")
        )
        self.session.add(new_seller)
        await self.session.commit()
        await self.session.refresh(new_seller)
        
        return new_seller
