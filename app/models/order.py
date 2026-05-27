from datetime import datetime
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Order(Base):
    __tablename__ = "orders"

    id:            Mapped[int]            = mapped_column(Integer, primary_key=True)
    customer_id:   Mapped[int]            = mapped_column(Integer,
                                                           ForeignKey("customers.id"),
                                                           nullable=False)
    product:       Mapped[str]            = mapped_column(String, nullable=False)
    quantity:      Mapped[int]            = mapped_column(Integer,
                                                           nullable=False, default=1)
    status:        Mapped[str]            = mapped_column(String,
                                                           default="Processing")
    delivery_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at:    Mapped[datetime]       = mapped_column(DateTime,
                                                           default=datetime.utcnow)

    customer = relationship("Customer", back_populates="orders", lazy="select")
    requests = relationship("OrderRequest", back_populates="order",
                            lazy="select")


class OrderRequest(Base):
    __tablename__ = "order_requests"

    id:         Mapped[int]            = mapped_column(Integer, primary_key=True)
    order_id:   Mapped[int]            = mapped_column(Integer,
                                                        ForeignKey("orders.id"),
                                                        nullable=False)
    type:       Mapped[str]            = mapped_column(String, nullable=False)
    reason:     Mapped[str | None]     = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime]       = mapped_column(DateTime,
                                                        default=datetime.utcnow)
    email_sent: Mapped[bool]           = mapped_column(Boolean, default=False)

    order = relationship("Order", back_populates="requests", lazy="select")
