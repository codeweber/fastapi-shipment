from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.dialects import postgresql
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from ..model.shipment_status import ShipmentStatus


class Base(DeclarativeBase, AsyncAttrs):
    pass

class Shipment(Base):
    __tablename__ = "shipment"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    content: Mapped[str]
    weight: Mapped[float]
    zip_code: Mapped[int]
    estimated_delivery: Mapped[datetime]

    client_contact_email: Mapped[str]
    client_contact_phone: Mapped[Optional[str]]

    seller_id: Mapped[UUID] = mapped_column(ForeignKey("seller.id"))
    delivery_partner_id: Mapped[UUID] = mapped_column(ForeignKey("delivery_partner.id"))

    created_at: Mapped[datetime] = mapped_column(default=datetime.now)

    seller: Mapped["Seller"] = relationship(back_populates="shipments", lazy="selectin")
    delivery_partner: Mapped["DeliveryPartner"] = relationship(back_populates="shipments", lazy="selectin")
    events: Mapped[List["ShipmentEvent"]] = relationship(back_populates="shipment", lazy="selectin")
    review: Mapped["Review"] = relationship(back_populates="shipment", lazy="selectin")

    @property
    def get_latest_event(self):
        self.events.sort(key=lambda x: x.created_at)
        return self.events[-1] if len(self.events) > 0 else None 
    
    @property
    def status(self):
        last_event = self.get_latest_event
        if last_event:
            return last_event.status
        else:
            return None
        


class ShipmentEvent(Base):
    __tablename__ = "shipment_event"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    status: Mapped[ShipmentStatus]
    location: Mapped[int]
    description: Mapped[Optional[str]]

    created_at: Mapped[datetime] = mapped_column(default=datetime.now)
    
    shipment_id: Mapped[UUID] = mapped_column(ForeignKey("shipment.id"))
    shipment: Mapped["Shipment"] = relationship(back_populates="events", lazy="selectin")

class UserMixin:
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str]
    email: Mapped[str] = mapped_column(unique=True)
    email_verified: Mapped[bool] = mapped_column(default=False)
    password_hash: Mapped[str]


class Seller(Base, UserMixin):
    __tablename__ = "seller"

    address: Mapped[Optional[str]]
    zip_code: Mapped[Optional[int]]

    created_at: Mapped[datetime] = mapped_column(default=datetime.now)

    shipments: Mapped[List["Shipment"]] = relationship(back_populates="seller", lazy="selectin")


class DeliveryPartner(Base, UserMixin):
    __tablename__ = "delivery_partner"

    created_at: Mapped[datetime] = mapped_column(default=datetime.now)

    max_shipment_capacity: Mapped[int]
    zip_codes: Mapped[List[int]] = mapped_column(postgresql.ARRAY(postgresql.INTEGER))

    shipments: Mapped[List["Shipment"]] = relationship(back_populates="delivery_partner", lazy="selectin")

class Review(Base):
    __tablename__ = "review"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)

    created_at: Mapped[datetime] = mapped_column(default=datetime.now)

    rating: Mapped[int]
    comment: Mapped[str | None] = mapped_column(default=None)

    shipment_id: Mapped[UUID] = mapped_column(ForeignKey("shipment.id"))
    shipment: Mapped["Shipment"] = relationship(back_populates="review", lazy="selectin")

    __table_args__ = (
        UniqueConstraint("shipment_id"),
    )