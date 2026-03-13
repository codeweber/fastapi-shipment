from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from ..database.session import get_session
from ..service.shipment import ShipmentService

SessionDep = Annotated[AsyncSession, Depends(get_session)]

def get_shipment_service(session: SessionDep):
    return ShipmentService(session)

ShipmentServiceDep = Annotated[ShipmentService, Depends(get_shipment_service)]