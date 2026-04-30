from typing import Annotated
from uuid import UUID
from jwt import InvalidTokenError
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, HTTPException, status

from app.database.model import DeliveryPartner, Seller
from app.database.redis import RedisDep
from app.service import utils
from app.service.delivery_partner import DeliveryPartnerService
from app.service.shipment_event import ShipmentEventService
from app.service.user import UserService

from ..database.session import get_session
from ..service.shipment import ShipmentService
from ..service.seller import SellerService
from ..core.security import oauth2_scheme_seller, oauth2_scheme_partner

SessionDep = Annotated[AsyncSession, Depends(get_session)]

def get_shipment_service(session: SessionDep):
    return ShipmentService(session, ShipmentEventService(session))

ShipmentServiceDep = Annotated[ShipmentService, Depends(get_shipment_service)]

def get_seller_service(session: SessionDep, redis: RedisDep):
    return SellerService(session, redis)

def get_partner_service(session: SessionDep, redis: RedisDep):
    return DeliveryPartnerService(session, redis)

SellerServiceDep = Annotated[SellerService, Depends(get_seller_service)]
PartnerServiceDep = Annotated[DeliveryPartnerService, Depends(get_partner_service)]

SellerTokenDep = Annotated[str, Depends(oauth2_scheme_seller)]
PartnerTokenDep = Annotated[str, Depends(oauth2_scheme_partner)]

credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

def _get_token_payload(token: str) -> dict:
    try: 
        payload = utils.decode_access_token(token)   
    except InvalidTokenError:
        raise credentials_exception
    return payload


def get_seller_token_payload(
        token: SellerTokenDep
) -> dict:
    return _get_token_payload(token)

def get_partner_token_payload(
        token: PartnerTokenDep
) -> dict:
    return _get_token_payload(token)


async def _get_current_user(
        token_payload: dict,
        user_service: UserService
):
    user_id = UUID(token_payload.get("user", {}).get("id"))
    if user_id is None:
        raise credentials_exception
    
    token_id = token_payload.get("jti")
    is_token_blacklisted = await user_service.is_token_blacklisted(token_id)
    if (not token_id) or (is_token_blacklisted):
        raise credentials_exception

    user = await user_service.get(user_id)

    if user is None:
        raise credentials_exception
    
    return user


async def get_current_seller(
    token_payload: Annotated[dict, Depends(get_seller_token_payload)],
    seller_service: SellerServiceDep
) -> Seller:
    return await _get_current_user(token_payload, seller_service)

CurrentSeller = Annotated[Seller, Depends(get_current_seller)]

async def get_current_partner(
    token_payload: Annotated[dict, Depends(get_partner_token_payload)],
    partner_service: PartnerServiceDep
) -> DeliveryPartner:
   return await _get_current_user(token_payload, partner_service)

CurrentPartner = Annotated[DeliveryPartner, Depends(get_current_partner)]