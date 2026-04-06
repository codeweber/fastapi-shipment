from uuid import UUID

from fastapi import APIRouter
from fastapi import HTTPException
from fastapi import status

from ..schema.shipment import Shipment, PreShipment
from ..dependencies import CurrentSeller, ShipmentServiceDep

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
async def create_shipment(pre_shipment: PreShipment, service: ShipmentServiceDep, seller: CurrentSeller) -> Shipment:
    result = await service.create(pre_shipment, seller)
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