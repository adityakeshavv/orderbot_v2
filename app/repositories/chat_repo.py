from datetime import datetime
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import ChatSession, Message


class ChatRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    # ── Sessions ───────────────────────────────────────────────────────────────

    async def create_session(self, session_id: str,
                              user_id: int) -> ChatSession:
        s = ChatSession(id=session_id, user_id=user_id)
        self.db.add(s)
        await self.db.flush()
        await self.db.refresh(s)
        return s

    async def get_session(self, session_id: str) -> Optional[ChatSession]:
        result = await self.db.execute(
            select(ChatSession).where(ChatSession.id == session_id)
        )
        return result.scalar_one_or_none()

    async def get_sessions_for_user(self, user_id: int) -> list[ChatSession]:
        result = await self.db.execute(
            select(ChatSession)
            .where(ChatSession.user_id == user_id)
            .order_by(ChatSession.updated_at.desc())
        )
        return list(result.scalars().all())

    async def delete_session(self, session: ChatSession) -> None:
        await self.db.delete(session)
        await self.db.flush()

    async def touch_session(self, session_id: str,
                             title: Optional[str] = None) -> None:
        session = await self.get_session(session_id)
        if session:
            session.updated_at = datetime.utcnow()
            if title and session.title == "New Chat":
                session.title = title[:80]
            await self.db.flush()

    async def rename_session(self, session: ChatSession,
                              title: str) -> None:
        session.title = title[:80]
        await self.db.flush()

    # ── Messages ───────────────────────────────────────────────────────────────

    async def save_message(self, session_id: str,
                            role: str, content: str) -> Message:
        msg = Message(session_id=session_id, role=role, content=content)
        self.db.add(msg)
        await self.db.flush()
        await self.db.refresh(msg)
        return msg

    async def get_messages(self, session_id: str) -> list[Message]:
        result = await self.db.execute(
            select(Message)
            .where(Message.session_id == session_id)
            .order_by(Message.created_at.asc())
        )
        return list(result.scalars().all())

    async def get_recent_messages(self, session_id: str,
                                   limit: int = 20) -> list[Message]:
        result = await self.db.execute(
            select(Message)
            .where(Message.session_id == session_id)
            .order_by(Message.created_at.desc())
            .limit(limit)
        )
        msgs = list(result.scalars().all())
        msgs.reverse()
        return msgs
