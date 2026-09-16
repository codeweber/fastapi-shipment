from random import randint
from typing import Optional
from uuid import UUID

from jwt import encode
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.model import Shipment, ShipmentEvent
from app.model.shipment_status import ShipmentStatus
from app.service.base import BaseService
from app.service.notification import NotificationService
from app.service.utils import encode_review_token, get_review_url
from app.settings import deployment_settings


class ShipmentEventService(BaseService):
    def __init__(self, session: AsyncSession, notification_service: NotificationService, redis: Redis):
        super().__init__(ShipmentEvent, session)
        self.notification_service = notification_service
        self.redis = redis

    async def create(
        self,
        shipment: Shipment,
        status: Optional[ShipmentStatus],
        location: Optional[int],
        description: Optional[str],
    ) -> ShipmentEvent:

        if status is None or location is None:
            latest_event = await self.get_latest_event(shipment)
            if latest_event:
                status = status if status else latest_event.status
                location = location if location else latest_event.location

        description = (
            description if description else self._generate_description(status, location)
        )

        new_event = ShipmentEvent(
            status=status,
            location=location,
            description=description,
            shipment_id=shipment.id,
        )

        await self._notify(shipment, status)

        return await self._add(new_event)

    async def get(self, id: UUID) -> Optional[ShipmentEvent]:
        return await self._get(id)

    async def get_latest_event(self, shipment: Shipment) -> ShipmentEvent | None:
        return shipment.get_latest_event

    @staticmethod
    def _generate_description(status: ShipmentStatus, location: int) -> str:
        match status:
            case ShipmentStatus.placed:
                return "assigned delivery partner"
            case ShipmentStatus.out_for_delivery:
                return "out for delivery"
            case ShipmentStatus.delivered:
                return "successfully delivered"
            case ShipmentStatus.cancelled:
                return "shipment cancelled"
            case _:
                return f"scanned at location {location}"


    async def _notify(self, shipment: Shipment, status: ShipmentStatus):

        subject: str = ""
        template_name: str = ""
        template_body: dict = {}

        match status:
            case ShipmentStatus.placed:
                subject="Your order is shipped"
                template_body={
                    "seller": shipment.seller.name,
                    "partner": shipment.delivery_partner.name
                }
                template_name="mail_placed.html"
            case ShipmentStatus.out_for_delivery:
                subject="Your order is out for delivery"
                template_body={
                    "seller": shipment.seller.name,
                }
                template_name="mail_out_for_delivery.html"

                verification_code = randint(100_000, 999_999)
                await self._set_verification_code(id = shipment.id, verification_code=verification_code)

                if shipment.client_contact_phone:
                    await self.notification_service.send_sms(
                        shipment.client_contact_phone,
                        body=f"Your order is arriving soon! Share the code {verification_code} to receive your package!"
                    )
                else:
                    template_body["verification_code"] = verification_code
            case ShipmentStatus.delivered:
                subject="Your order has been delivered"
                template_body={
                    "seller": shipment.seller.name,
                    "review_url": get_review_url(token=encode_review_token(shipment_id=shipment.id))
                }
                template_name="mail_delivered.html"
            case _:
                return None
            
        self.notification_service.send_email_with_template(
                recipients=[shipment.client_contact_email],
                subject=subject,
                template_body=template_body,
                template_name=template_name
            )
        
    def get_verification_code_key(self, id: UUID) -> str:
        return f"vc_{id}"
        
    async def _set_verification_code(self, id: UUID, verification_code: int) -> None:
        await self.redis.set(self.get_verification_code_key(id), str(verification_code))

    async def _get_verification_code(self, id: UUID) -> Optional[int]:
        value = await self.redis.get(self.get_verification_code_key(id))

        if value:
            try:
                verification_code = int(value)
            except ValueError:
                verification_code = None
        else:
            verification_code = None

        return verification_code
    
    async def is_verification_code_correct(self, shipment: Shipment, verification_code: int) -> bool:
        expected_verification_code = await self._get_verification_code(shipment.id)

        if (verification_code is None) or (expected_verification_code is None):
            return False 
        else:
            return expected_verification_code == verification_code
            

