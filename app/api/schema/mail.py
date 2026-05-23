
from pydantic import BaseModel, EmailStr


class Mail(BaseModel):
    recipients: list[EmailStr]
    subject: str
    body: str