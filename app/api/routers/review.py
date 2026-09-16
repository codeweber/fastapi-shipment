from typing import Annotated

from fastapi import APIRouter, Form, HTTPException, Request, status
from fastapi.templating import Jinja2Templates

from app.api.dependencies import ShipmentServiceDep
from app.api.schema.shipment import ShipmentReview
from app.service.utils import TEMPLATES_DIR, decode_review_token, get_review_url

router = APIRouter(prefix="/review", tags=["review"])
templates = Jinja2Templates(directory=TEMPLATES_DIR)

@router.get("/")
async def get_review_form(request: Request, token: str):
    context = {
        "review_url": get_review_url(token)
    }

    return templates.TemplateResponse(
        request=request,
        name="review.html",
        context=context
    )


@router.post("/")
async def submit_review(token: str, review: Annotated[ShipmentReview, Form()], service: ShipmentServiceDep):

    shipment_id = decode_review_token(token)
    if not shipment_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired or is invalid"
        )

    review = await service.review(shipment_id, review)

    if not review:
        raise HTTPException(
            status=status.HTTP_400_BAD_REQUEST,
            detail="Token invalid"
        )

    return { "detail": "Review submitted successfully." }