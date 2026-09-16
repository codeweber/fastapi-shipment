from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Form, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from pydantic import EmailStr

from app.api.dependencies import SellerServiceDep, get_seller_token_payload
from app.api.schema.seller import SellerRead, SellerWithPassword, Token
from app.model.errors import UnauthorizedException
from app.service.utils import TEMPLATES_DIR
from app.settings import deployment_settings

router = APIRouter(prefix="/seller", tags=["seller"])
templates = Jinja2Templates(directory=TEMPLATES_DIR)

@router.post("/signup", response_model=SellerRead)
async def create_seller(body: SellerWithPassword, service: SellerServiceDep):
    return await service.create(body)

@router.post("/token")
async def login_seller(
    form_details: Annotated[OAuth2PasswordRequestForm, Depends()],
    service: SellerServiceDep,
) -> Token:
    
    try:
        token = await service.token(form_details.username, form_details.password)
    except UnauthorizedException as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"{e!r}"
        )


    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username or password are incorrect.",
        )

    return Token(access_token=token, token_type="bearer")

@router.post("/logout")
async def logout_seller(
    token_payload: Annotated[dict, Depends(get_seller_token_payload)],
    service: SellerServiceDep,
) -> None:
    token_id = token_payload.get("jti")
    expiry_time = datetime.fromtimestamp(token_payload.get("exp"), tz=UTC)
    await service.blacklist_token(token_id, expiry_time)

@router.get("/verify")
async def verify_email_seller(
    token: str,
    service: SellerServiceDep
):
    id = await service.verify_email(token)

    if not id:
        raise HTTPException(
            status=status.HTTP_400_BAD_REQUEST,
            detail="Invalid token"
        )

    return {"detail": f"Email verified for user {id}"}

@router.get("/forgot_password")
async def forgot_password_seller(
    email: EmailStr,
    service: SellerServiceDep
):
    id = await service.send_password_reset(email, router.prefix)

    if not id:
        raise HTTPException(
            status=status.HTTP_400_BAD_REQUEST,
            detail=f"Email address ${email} could not be found"
        )

    return {"detail": f"Password reset sent for user {id}"}

@router.get("/reset_password")
async def reset_password_form_seller(
    request: Request,
    token: str,

):
    return templates.TemplateResponse(
        request=request,
        name="password/reset.html",
        context={
            "reset_url": f"http://{deployment_settings.HOST}:{deployment_settings.PORT}{router.prefix}/reset_password?token={token}"
        }
    )

@router.post("/reset_password")
async def reset_password_seller(
    request: Request,
    password: Annotated[str, Form()],
    token: str,
    service: SellerServiceDep
):

    maybe_user = await service.reset_password(token, password=password)

    return templates.TemplateResponse(
        request=request,
        name="password/reset_success.html" if maybe_user else "password/reset_failed.html"
    )