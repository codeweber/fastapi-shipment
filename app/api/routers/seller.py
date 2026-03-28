from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import status

from app.api.dependencies import SellerServiceDep
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
    
    return Token(token, token_type="bearer")
