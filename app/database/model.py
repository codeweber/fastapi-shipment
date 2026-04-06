from sqlalchemy import ForeignKey
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column, relationship
from datetime import datetime
from uuid import UUID, uuid4

from ..model.shipment_status import ShipmentStatus

class Base(DeclarativeBase, AsyncAttrs):
    pass

class Shipment(Base):
    __tablename__ = "shipment"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    content: Mapped[str]
    weight: Mapped[float]
    estimated_delivery: Mapped[datetime]
    status: Mapped[ShipmentStatus]
    seller_id: Mapped[UUID] = mapped_column(ForeignKey("seller.id"))

    seller: Mapped["Seller"] = relationship(back_populates="shipments")

class Seller(Base):
    __tablename__ = "seller"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str]
    email: Mapped[str]
    password_hash: Mapped[str]

    shipments: Mapped["Shipment"] = relationship(back_populates="seller")
