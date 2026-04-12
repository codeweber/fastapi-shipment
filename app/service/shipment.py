from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta

from ..database.model import DeliveryPartner, Seller, Shipment, ShipmentStatus
from ..api.schema.shipment import PreShipment

class ShipmentService():

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, details: PreShipment, seller: Seller, delivery_partner: DeliveryPartner) -> Shipment:
        new_shipment = Shipment(
            **details.model_dump(),
            status = ShipmentStatus.placed,
            estimated_delivery = datetime.now() + timedelta(days = 3),
            seller_id = seller.id,
            delivery_partner_id = delivery_partner.id
        )
        self.session.add(new_shipment)
        await self.session.commit()
        await self.session.refresh(new_shipment)
        
        return new_shipment

    async def get(self, id: UUID) -> Shipment | None:
        return (await self.session.get(Shipment, id))
    
    async def delete(self, id: UUID, seller: Seller) -> int | None:
        entity_to_delete = await self.get(id)

        if entity_to_delete is None or (entity_to_delete.seller_id != seller.id):
            return None 
        
        await self.session.delete(entity_to_delete)
        await self.session.commit()

        return 1
        
    

