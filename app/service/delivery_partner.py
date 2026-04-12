from typing import Optional
from uuid import UUID

from redis.asyncio import Redis
from sqlalchemy import select, any_
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schema.delivery_partner import DeliveryPartnerWithPassword
from app.database.model import DeliveryPartner
from app.model.shipment_status import ShipmentStatus
from app.service.user import UserService


class DeliveryPartnerService(UserService):
    def __init__(self, session: AsyncSession, redis: Redis):
        super().__init__(user_type=DeliveryPartner, session=session, redis=redis)

    async def create(self, details: DeliveryPartnerWithPassword) -> DeliveryPartner:
        new_partner = DeliveryPartner(
            **details.model_dump(exclude=["password"]),
            password_hash=self.hash(details.password),
        )
        self.session.add(new_partner)
        await self.session.commit()
        await self.session.refresh(new_partner)

        return new_partner

    async def get(self, id: UUID) -> Optional[DeliveryPartner]:
        return await self.session.get(DeliveryPartner, id)

    async def get_partners_by_zip(self, zip: int) -> list[DeliveryPartner]:
        stmt = select(DeliveryPartner).where(zip == any_(DeliveryPartner.zip_codes))
        result = await self.session.scalars(stmt)
        return result.all()

    async def get_eligible_partner(self, zip: int) -> Optional[DeliveryPartner]:
        for partner in await self.get_partners_by_zip(zip):
            num_active_shipments = sum(
                1
                for _ in (
                    shipment
                    for shipment in partner.shipments
                    if shipment.status != ShipmentStatus.deliverd
                )
            )
            if num_active_shipments < partner.max_shipment_capacity:
                return partner
        return None
