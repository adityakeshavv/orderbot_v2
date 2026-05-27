from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id:         Mapped[str]      = mapped_column(String, primary_key=True)
    user_id:    Mapped[int]      = mapped_column(Integer,
                                                  ForeignKey("users.id"),
                                                  nullable=False)
    title:      Mapped[str]      = mapped_column(String(120),
                                                  default="New Chat")
    created_at: Mapped[datetime] = mapped_column(DateTime,
                                                  default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime,
                                                  default=datetime.utcnow)

    user     = relationship("User", back_populates="sessions", lazy="select")
    messages = relationship("Message", back_populates="session",
                            order_by="Message.created_at",
                            cascade="all, delete-orphan", lazy="select")


class Message(Base):
    __tablename__ = "messages"

    id:         Mapped[int]      = mapped_column(Integer, primary_key=True)
    session_id: Mapped[str]      = mapped_column(String,
                                                  ForeignKey("chat_sessions.id",
                                                             ondelete="CASCADE"),
                                                  nullable=False)
    role:       Mapped[str]      = mapped_column(String(10), nullable=False)
    content:    Mapped[str]      = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime,
                                                  default=datetime.utcnow)

    session = relationship("ChatSession", back_populates="messages",
                           lazy="select")
