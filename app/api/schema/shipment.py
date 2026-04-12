from uuid import UUID

from pydantic import BaseModel
from datetime import datetime

from ...model.shipment_status import ShipmentStatus

class PreShipment(BaseModel):
    content: str 
    weight: float
    zip_code: int

class Shipment(PreShipment):
    id: UUID
    estimated_delivery: datetime
    status: ShipmentStatus

