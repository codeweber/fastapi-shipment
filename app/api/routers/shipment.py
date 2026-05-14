from uuid import UUID

from fastapi import APIRouter
from fastapi import HTTPException
from fastapi import status

from app.model.errors import UnauthorizedException

from ..schema.shipment import Shipment, ShipmentCreate, ShipmentUpdate
from ..dependencies import CurrentPartner, CurrentSeller, PartnerServiceDep, ShipmentServiceDep

router = APIRouter(prefix="/shipment", tags=["shipment"])

@router.get("/{id}", response_model=Shipment)
async def get_shipment(id: UUID, service: ShipmentServiceDep, seller: CurrentSeller):
    result = await service.get(id)

    if result is None or (result.seller_id != seller.id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Given id {id} does not exist"
        )

    return result


@router.post("/")
async def create_shipment(pre_shipment: ShipmentCreate, service: ShipmentServiceDep, seller: CurrentSeller, partner_service: PartnerServiceDep) -> Shipment:
    delivery_partner = await partner_service.get_eligible_partner(pre_shipment.zip_code)

    if delivery_partner is None:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail=f"Could not find an eligible delivery partner for shipment with zip code {pre_shipment.zip_code}"
        )

    result = await service.create(pre_shipment, seller, delivery_partner)
    return result

@router.patch("/{id}", response_model=Shipment)
async def update_shipment(id: UUID, shipment_update: ShipmentUpdate, partner: CurrentPartner, service: ShipmentServiceDep):
    update = shipment_update.model_dump(exclude_none=True)
    if not update:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No data provided to update"
        )
    
    return await service.update(id, shipment_update, partner)

@router.get("/{id}/cancel", response_model=Shipment)
async def cancel_shipment(id: UUID, service: ShipmentServiceDep, seller: CurrentSeller) -> None:
    
    try:
        result = await service.cancel(id, seller)
    except UnauthorizedException as e:
        raise HTTPException(
            status_code=status.HTTP_403_UNAUTHORIZED,
            detail=f"{e!r}"
        )

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Given id {id} does not exist for seller with id {seller.id}"
        )

    return result