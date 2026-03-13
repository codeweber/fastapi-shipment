from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta

from ..database.model import Shipment, ShipmentStatus
from ..api.schema.shipment import PreShipment

class ShipmentService():

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, details: PreShipment) -> Shipment:
        new_shipment = Shipment(
            **details.model_dump(),
            status = ShipmentStatus.placed,
            estimated_delivery = datetime.now() + timedelta(days = 3)
        )
        self.session.add(new_shipment)
        await self.session.commit()
        await self.session.refresh(new_shipment)
        
        return new_shipment

    async def get(self, id: int) -> Shipment | None:
        return (await self.session.get(Shipment, id))
    
    async def delete(self, id: int) -> int | None:
        entity_to_delete = await self.get(id)

        if entity_to_delete is None:
            return None 
        
        await self.session.delete(entity_to_delete)
        await self.session.commit()

        return 1
        
    

