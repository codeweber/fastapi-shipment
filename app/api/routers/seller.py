from datetime import UTC, datetime
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import status

from app.api.dependencies import SellerServiceDep, get_token_payload
from app.api.schema.seller import SellerRead, SellerWithPassword, Token

router = APIRouter(prefix="/seller", tags=["seller"])


@router.post("/signup", response_model=SellerRead)
async def create_seller(body: SellerWithPassword, service: SellerServiceDep):
    return await service.create(body)

@router.post("/token")
async def login_seller(
    form_details: Annotated[OAuth2PasswordRequestForm, Depends()],
    service: SellerServiceDep,
) -> Token:
    token = await service.token(form_details.username, form_details.password)

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username or password are incorrect.",
        )

    return Token(access_token=token, token_type="bearer")

@router.post("/logout")
async def logout_sellet(
    token_payload: Annotated[dict, Depends(get_token_payload)],
    service: SellerServiceDep,
) -> None:
    token_id = token_payload.get("jti")
    expiry_time = datetime.fromtimestamp(token_payload.get("exp"), tz=UTC)
    await service.blacklist_token(token_id, expiry_time)

