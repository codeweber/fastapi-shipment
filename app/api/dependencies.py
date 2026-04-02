from typing import Annotated
from jwt import InvalidTokenError
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, HTTPException, status

from app.database.model import Seller
from app.database.redis import RedisDep
from app.service import utils

from ..database.session import get_session
from ..service.shipment import ShipmentService
from ..service.seller import SellerService
from ..core.security import oauth2_scheme

SessionDep = Annotated[AsyncSession, Depends(get_session)]

def get_shipment_service(session: SessionDep):
    return ShipmentService(session)

ShipmentServiceDep = Annotated[ShipmentService, Depends(get_shipment_service)]

def get_seller_service(session: SessionDep, redis: RedisDep):
    return SellerService(session, redis)

SellerServiceDep = Annotated[SellerService, Depends(get_seller_service)]

TokenDep = Annotated[str, Depends(oauth2_scheme)]

credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

def get_token_payload(
        token: TokenDep
) -> dict:
    try: 
        payload = utils.decode_access_token(token)   
    except InvalidTokenError:
        raise credentials_exception
    return payload
    

async def get_current_seller(
    token_payload: Annotated[dict, Depends(get_token_payload)],
    seller_service: SellerServiceDep
) -> Seller:
    
    seller_id = token_payload.get("user", {}).get("id")
    if seller_id is None:
        raise credentials_exception
    
    token_id = token_payload.get("jti")
    is_token_blacklisted = await seller_service.is_token_blacklisted(token_id)
    if (not token_id) or (is_token_blacklisted):
        raise credentials_exception

    seller = await seller_service.get(seller_id)

    if seller is None:
        raise credentials_exception
    
    return seller

CurrentSeller = Annotated[Seller, Depends(get_current_seller)]