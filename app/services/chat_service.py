import uuid
from typing import Optional

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User
from app.repositories import ChatRepository
from app.schemas import SessionOut, SessionDetailOut, MessageOut


class ChatService:

    def __init__(self, db: AsyncSession):
        self.repo = ChatRepository(db)

    async def create_session(self, user: User) -> SessionOut:
        s = await self.repo.create_session(str(uuid.uuid4()), user.id)
        return SessionOut.model_validate(s)

    async def list_sessions(self, user: User) -> list[SessionOut]:
        sessions = await self.repo.get_sessions_for_user(user.id)
        return [SessionOut.model_validate(s) for s in sessions]

    async def get_session(self, session_id: str,
                           user: User) -> SessionDetailOut:
        s = await self.repo.get_session(session_id)
        if not s:
            raise HTTPException(404, "Session not found")
        if s.user_id != user.id:
            raise HTTPException(403, "Access denied")
        msgs = await self.repo.get_messages(session_id)
        return SessionDetailOut(
            id=s.id,
            title=s.title,
            created_at=s.created_at,
            updated_at=s.updated_at,
            messages=[MessageOut.model_validate(m) for m in msgs],
        )

    async def delete_session(self, session_id: str, user: User) -> None:
        s = await self.repo.get_session(session_id)
        if not s:
            raise HTTPException(404, "Session not found")
        if s.user_id != user.id:
            raise HTTPException(403, "Access denied")
        await self.repo.delete_session(s)

    async def rename_session(self, session_id: str,
                              title: str, user: User) -> SessionOut:
        s = await self.repo.get_session(session_id)
        if not s or s.user_id != user.id:
            raise HTTPException(404, "Session not found")
        await self.repo.rename_session(s, title)
        return SessionOut.model_validate(s)

    async def validate_session(self, session_id: str,
                                user: Optional[User]) -> None:
        """Check session exists and belongs to user."""
        s = await self.repo.get_session(session_id)
        if not s:
            raise HTTPException(404, "Session not found")
        if user and s.user_id != user.id:
            raise HTTPException(403, "Access denied")
