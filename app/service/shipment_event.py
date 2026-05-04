from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.database.model import Shipment, ShipmentEvent
from app.model.shipment_status import ShipmentStatus
from app.service.base import BaseService


class ShipmentEventService(BaseService):
    def __init__(self, session: AsyncSession):
        super().__init__(ShipmentEvent, session)

    async def create(
        self,
        shipment: Shipment,
        status: Optional[ShipmentStatus],
        location: Optional[int],
        description: Optional[str],
    ) -> ShipmentEvent:

        if status is None or location is None:
            latest_event = await self.get_latest_event(shipment)
            if latest_event:
                status = status if status else latest_event.status
                location = location if location else latest_event.location

        description = (
            description if description else self._generate_description(status, location)
        )

        new_event = ShipmentEvent(
            status=status,
            location=location,
            description=description,
            shipment_id=shipment.id,
        )
        return await self._add(new_event)

    async def get(self, id: UUID) -> Optional[ShipmentEvent]:
        return await self._get(id)

    async def get_latest_event(self, shipment: Shipment) -> ShipmentEvent | None:
        return shipment.get_latest_event

    @staticmethod
    def _generate_description(status: ShipmentStatus, location: int) -> str:
        match status:
            case ShipmentStatus.placed:
                return "assigned delivery partner"
            case ShipmentStatus.out_for_delivery:
                return "out for delivery"
            case ShipmentStatus.delivered:
                return "successfully delivered"
            case ShipmentStatus.cancelled:
                return "shipment cancelled"
            case _:
                return f"scanned at location {location}"
