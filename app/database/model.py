from typing import List

from sqlalchemy import ForeignKey
from sqlalchemy.dialects import postgresql
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
    delivery_partner_id: Mapped[UUID] = mapped_column(ForeignKey("delivery_partner.id"))

    created_at: Mapped[datetime] = mapped_column(default=datetime.now)

    seller: Mapped["Seller"] = relationship(back_populates="seller.shipments")
    delivery_partner: Mapped["DeliveryPartner"] = relationship(back_populates="delivery_partner.shipments")

class Seller(Base):
    __tablename__ = "seller"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str]
    email: Mapped[str]
    password_hash: Mapped[str]

    created_at: Mapped[datetime] = mapped_column(default=datetime.now)

    shipments: Mapped[List["Shipment"]] = relationship(back_populates="seller")


class DeliveryPartner(Base):
    __tablename__ = "delivery_partner"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str]
    email: Mapped[str]
    password_hash: Mapped[str]

    created_at: Mapped[datetime] = mapped_column(default=datetime.now)

    max_shipment_capacity: Mapped[int]
    zip_codes: Mapped[List[int]] = mapped_column(postgresql.ARRAY(postgresql.INTEGER))

    shipments: Mapped[List["Shipment"]] = relationship(back_populates="delivery_partner")

