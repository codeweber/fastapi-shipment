from uuid import UUID

from fastapi import APIRouter
from fastapi import HTTPException
from fastapi import status

from ..schema.shipment import Shipment, PreShipment
from ..dependencies import CurrentSeller, PartnerServiceDep, ShipmentServiceDep

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
async def create_shipment(pre_shipment: PreShipment, service: ShipmentServiceDep, seller: CurrentSeller, partner_service: PartnerServiceDep) -> Shipment:
    delivery_partner = await partner_service.get_eligible_partner(pre_shipment.zip_code)

    if delivery_partner is None:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail=f"Could not find an eligible delivery partner for shipment with zip code {pre_shipment.zip_code}"
        )

    result = await service.create(pre_shipment, seller, delivery_partner)
    return result


@router.delete("/{id}")
async def delete_shipment(id: UUID, service: ShipmentServiceDep, seller: CurrentSeller) -> None:
    result = await service.delete(id, seller)

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Given id {id} does not exist for seller with id {seller.id}"
        )

    return None