import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.api.dependencies import PartnerServiceDep, get_partner_token_payload
from app.api.schema.delivery_partner import DeliveryPartnerRead, DeliveryPartnerWithPassword, Token

router = APIRouter(prefix="/partner", tags=["partner"])

@router.post("/signup", response_model=DeliveryPartnerRead)
async def create_partner(body: DeliveryPartnerWithPassword, service: PartnerServiceDep):
    return await service.create(body)

@router.post("/token")
async def login_partner(
    form_details: Annotated[OAuth2PasswordRequestForm, Depends()],
    service: PartnerServiceDep
) -> Token:
    token = await service.token(form_details.username, form_details.password)

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username or password are incorrect.",
        )

    return Token(access_token=token, token_type="bearer")

@router.post("/logout")
async def logout_partner(
    token_payload: Annotated[dict, Depends(get_partner_token_payload)],
    service: PartnerServiceDep,
) -> None:
    token_id = token_payload.get("jti")
    expiry_time = datetime.fromtimestamp(token_payload.get("exp"), tz=datetime.UTC)
    await service.blacklist_token(token_id, expiry_time)