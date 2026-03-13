from fastapi import APIRouter
from fastapi import HTTPException
from fastapi import status

from .schema.shipment import Shipment, PreShipment
from .dependencies import ShipmentServiceDep

router = APIRouter(prefix="/shipment")

@router.get("/{id}", response_model=Shipment)
async def get_shipment(id: int, service: ShipmentServiceDep):
    result = await service.get(id)

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Given id {id} does not exist"
        )

    return result


@router.post("/")
async def create_shipment(pre_shipment: PreShipment, service: ShipmentServiceDep) -> Shipment:
    result = await service.create(pre_shipment)
    return result


@router.delete("/{id}")
async def delete_shipment(id: int, service: ShipmentServiceDep) -> None:
    result = await service.delete(id)

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Given id {id} does not exist"
        )

    return None