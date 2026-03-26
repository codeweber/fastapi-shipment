from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from datetime import datetime

from ..model.shipment_status import ShipmentStatus

class Base(DeclarativeBase, AsyncAttrs):
    pass

class Shipment(Base):
    __tablename__ = "shipment"

    id: Mapped[int] = mapped_column(primary_key=True)
    content: Mapped[str]
    weight: Mapped[float]
    estimated_delivery: Mapped[datetime]
    status: Mapped[ShipmentStatus]

class Seller(Base):
    __tablename__ = "seller"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    email: Mapped[str]
    password_hash: Mapped[str]
