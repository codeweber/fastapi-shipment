from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field
from datetime import datetime

from app.api.schema.shipment_event import ShipmentEvent

from ...model.shipment_status import ShipmentStatus

class PreShipment(BaseModel):
    content: str 
    weight: float
    zip_code: int

class ShipmentCreate(PreShipment):
    client_contact_email: EmailStr

class Shipment(PreShipment):
    id: UUID
    estimated_delivery: datetime
    events: list[ShipmentEvent]

class ShipmentUpdate(BaseModel):
    location: Optional[int] = Field(default=None)
    status: Optional[ShipmentStatus] = Field(default=None)
    description: Optional[str] = Field(default=None)
    estimated_delivery: Optional[None] = Field(default=None)

