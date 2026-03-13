from pydantic import BaseModel
from datetime import datetime

from ...model.shipment_status import ShipmentStatus

class PreShipment(BaseModel):
    content: str 
    weight: float


class Shipment(PreShipment):
    id: int
    estimated_delivery: datetime
    status: ShipmentStatus

