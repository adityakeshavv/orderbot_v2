from datetime import datetime
from sqlalchemy import Boolean, DateTime, Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id:              Mapped[int]      = mapped_column(Integer, primary_key=True)
    name:            Mapped[str]      = mapped_column(String, nullable=False)
    email:           Mapped[str]      = mapped_column(String, unique=True,
                                                       nullable=False, index=True)
    hashed_password: Mapped[str]      = mapped_column(String, nullable=False)
    role:            Mapped[str]      = mapped_column(String, default="customer")
    is_active:       Mapped[bool]     = mapped_column(Boolean, default=True)
    created_at:      Mapped[datetime] = mapped_column(DateTime,
                                                       default=datetime.utcnow)

    customer = relationship("Customer", back_populates="user",
                            uselist=False, lazy="select")
    sessions = relationship("ChatSession", back_populates="user",
                            lazy="select")


class Customer(Base):
    __tablename__ = "customers"

    id:      Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"),
                                          nullable=False, unique=True)
    name:    Mapped[str] = mapped_column(String, nullable=False)
    email:   Mapped[str] = mapped_column(String, unique=True, nullable=False)

    user   = relationship("User", back_populates="customer", lazy="select")
    orders = relationship("Order", back_populates="customer", lazy="select")
