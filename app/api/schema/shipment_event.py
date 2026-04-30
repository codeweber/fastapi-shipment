
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from app.model.shipment_status import ShipmentStatus


class ShipmentEvent(BaseModel):
    id: UUID
    status: Optional[ShipmentStatus]
    location: Optional[int]
    description: Optional[str]
    created_at: datetime