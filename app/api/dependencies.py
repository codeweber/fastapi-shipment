from typing import Annotated
from jwt import InvalidTokenError
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, HTTPException, status

from app.database.model import Seller
from app.service import utils

from ..database.session import get_session
from ..service.shipment import ShipmentService
from ..service.seller import SellerService
from ..core.security import oauth2_scheme

SessionDep = Annotated[AsyncSession, Depends(get_session)]

def get_shipment_service(session: SessionDep):
    return ShipmentService(session)

ShipmentServiceDep = Annotated[ShipmentService, Depends(get_shipment_service)]

def get_seller_service(session: SessionDep):
    return SellerService(session)

SellerServiceDep = Annotated[SellerService, Depends(get_seller_service)]

async def get_current_seller(
    token: Annotated[str, Depends(oauth2_scheme)],
    seller_service: SellerServiceDep
) -> Seller:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:    
        seller_id = utils.decode_access_token(token).get("user", {}).get("id")
        if seller_id is None:
            print("seller_id is None")
            return credentials_exception
    except InvalidTokenError:
        raise credentials_exception

    seller = await seller_service.get(seller_id)

    if seller is None:
        print("Error: seller not found")
        raise credentials_exception
    
    return seller

CurrentSeller = Annotated[Seller, Depends(get_current_seller)]