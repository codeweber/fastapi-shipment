
from pydantic import BaseModel, EmailStr


class DeliveryPartnerBase(BaseModel):
    name: str 
    email: EmailStr
    zip_codes: list[int]
    max_shipment_capacity: int
    
class DeliveryPartnerRead(DeliveryPartnerBase):
    pass

class DeliveryPartnerWithPassword(DeliveryPartnerBase):
    password: str


class Token(BaseModel):
    access_token: str 
    token_type: str
