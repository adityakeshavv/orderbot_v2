from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models import User
from app.schemas import SessionOut, SessionDetailOut, RenameRequest
from app.services import ChatService

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.post("", response_model=SessionOut, status_code=201)
async def create_session(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await ChatService(db).create_session(current_user)


@router.get("", response_model=list[SessionOut])
async def list_sessions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await ChatService(db).list_sessions(current_user)


@router.get("/{session_id}", response_model=SessionDetailOut)
async def get_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await ChatService(db).get_session(session_id, current_user)


@router.delete("/{session_id}", status_code=204)
async def delete_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await ChatService(db).delete_session(session_id, current_user)


@router.patch("/{session_id}", response_model=SessionOut)
async def rename_session(
    session_id: str,
    body: RenameRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await ChatService(db).rename_session(
        session_id, body.title, current_user)
