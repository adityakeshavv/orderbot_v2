from datetime import datetime
from typing import Optional
from pydantic import BaseModel, field_validator


class ChatRequest(BaseModel):
    message:    str
    session_id: str

    @field_validator("message")
    @classmethod
    def message_not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Message cannot be empty")
        if len(v) > 2000:
            raise ValueError("Message too long (max 2000 chars)")
        return v


class RenameRequest(BaseModel):
    title: str

    @field_validator("title")
    @classmethod
    def title_not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Title cannot be empty")
        return v


class MessageOut(BaseModel):
    id:         int
    role:       str
    content:    str
    created_at: datetime

    model_config = {"from_attributes": True}


class SessionOut(BaseModel):
    id:         str
    title:      str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class SessionDetailOut(SessionOut):
    messages: list[MessageOut] = []
