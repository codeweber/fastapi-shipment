from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from ..database.session import get_session
from ..service.shipment import ShipmentService
from ..service.seller import SellerService

SessionDep = Annotated[AsyncSession, Depends(get_session)]

def get_shipment_service(session: SessionDep):
    return ShipmentService(session)

ShipmentServiceDep = Annotated[ShipmentService, Depends(get_shipment_service)]

def get_seller_service(session: SessionDep):
    return SellerService(session)

SellerServiceDep = Annotated[SellerService, Depends(get_seller_service)]