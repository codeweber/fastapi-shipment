from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta

from app.model.shipment_status import ShipmentStatus
from app.service.base import BaseService
from app.service.shipment_event import ShipmentEventService

from ..database.model import DeliveryPartner, Seller, Shipment
from ..api.schema.shipment import PreShipment, ShipmentUpdate

class ShipmentService(BaseService):

    def __init__(self, session: AsyncSession, event_service: ShipmentEventService):
        super().__init__(Shipment, session)
        self.event_service = event_service

    async def create(self, details: PreShipment, seller: Seller, delivery_partner: DeliveryPartner) -> Shipment:
        new_shipment = Shipment(
            **details.model_dump(),
            estimated_delivery = datetime.now() + timedelta(days = 3),
            seller_id = seller.id,
            delivery_partner_id = delivery_partner.id
        )

        shipment = await self._add(new_shipment)

        await self.event_service.create(
            shipment,
            status=ShipmentStatus.placed,
            # note the we use the zip code of the delivery because it must be defined
            # it also isn't perhaps well defined what the "location" of a service event is at the time the order is placed
            location=details.zip_code, 
            description=f"order placed with delivery partner {delivery_partner.name}"
        )

        return shipment
    
    async def get(self, id: UUID) -> Shipment | None:
        return await self._get(id)
    
    async def delete(self, id: UUID, seller: Seller) -> int | None:
        entity_to_delete = await self.get(id)

        if entity_to_delete is None or (entity_to_delete.seller_id != seller.id):
            return None 
        
        await self.session.delete(entity_to_delete)
        await self.session.commit()

        return 1
    
    async def update(self, id: UUID, shipment_update: ShipmentUpdate, delivery_partner: DeliveryPartner) -> Shipment | None:
        shipment = await self.get(id)

        if not shipment:
            return None

        if shipment.delivery_partner_id != delivery_partner.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Delivery Partner is not permitted to update this shipment"
            )
        
        if shipment_update.estimated_delivery:
            shipment.estimated_delivery = shipment_update.estimated_delivery

        update = shipment_update.model_dump(exclude_none=True, exclude={'estimated_delivery'})

        if len(update) > 0:
            await self.event_service.create(
                shipment,
                **update
            )

        return await self._add(shipment)
        
    

