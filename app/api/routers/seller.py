from fastapi import APIRouter

from app.api.dependencies import SellerServiceDep
from app.api.schema.seller import SellerRead, SellerWithPassword

router = APIRouter(prefix="/seller", tags=["seller"])

@router.post("/signup", response_model=SellerRead)
async def create_seller(body: SellerWithPassword, service: SellerServiceDep):
    return await service.create(body)
