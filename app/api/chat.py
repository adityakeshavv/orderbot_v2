import json
import logging
from typing import Optional

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from openai import AsyncOpenAI

from app.agent import OrderBotAgent
from app.core.config import settings
from app.core.database import get_db
from app.core.security import get_current_user_optional
from app.models import User
from app.repositories import ChatRepository, UserRepository
from app.schemas import ChatRequest
from app.services import ChatService

router = APIRouter(prefix="/chat", tags=["chat"])
log    = logging.getLogger("orderbot.api.chat")
client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)


async def _generate_title(user_message: str, bot_response: str) -> str:
    """Ask GPT to generate a short descriptive title for the conversation."""
    try:
        resp = await client.chat.completions.create(
            model="gpt-4o-mini",
            max_tokens=12,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Generate a short 3-5 word title for this conversation. "
                        "Return ONLY the title, no quotes, no punctuation at end."
                        "Examples: 'Track Order Status', 'Speed Up Steel Order', "
                        "'Cancel Pipe Order', 'Place New Indent'"
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"User said: {user_message}\n"
                        f"Bot replied: {bot_response[:200]}"
                    ),
                },
            ],
        )
        return resp.choices[0].message.content.strip()[:80]
    except Exception:
        return user_message[:60]


def _sse(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"


@router.post("")
async def chat(
    body: ChatRequest,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db),
):
    chat_repo = ChatRepository(db)
    user_repo = UserRepository(db)

    # Auto-create session if it doesn't exist yet
    session = await chat_repo.get_session(body.session_id)
    if not session:
        if not current_user:
            from fastapi import HTTPException
            raise HTTPException(401, "Not authenticated")
        session = await chat_repo.create_session(
            body.session_id, current_user.id)

    # Validate ownership
    if current_user and session.user_id != current_user.id:
        from fastapi import HTTPException
        raise HTTPException(403, "Access denied")

    # Resolve customer
    customer = None
    if current_user:
        customer = await user_repo.get_customer_by_user_id(current_user.id)

    # Check if this is the first message in this session
    existing = await chat_repo.get_messages(body.session_id)
    is_first_message = len(existing) == 0

    # Save user message
    await chat_repo.save_message(body.session_id, "user", body.message)
    await chat_repo.touch_session(body.session_id)

    full_response: list[str] = []

    async def event_stream():
        try:
            agent = OrderBotAgent(db, body.session_id, customer)
            async for chunk in agent.stream(body.message):
                full_response.append(chunk)
                yield _sse("token", {"token": chunk})

        except Exception as exc:
            log.exception("Stream error: %s", exc)
            err = "⚠️ Something went wrong. Please try again."
            full_response.append(err)
            yield _sse("token", {"token": err})

        finally:
            complete = "".join(full_response)
            if complete:
                await chat_repo.save_message(
                    body.session_id, "bot", complete)

            # Generate smart title from first exchange only
            if is_first_message and complete:
                title = await _generate_title(body.message, complete)
                await chat_repo.rename_session(session, title)

            yield _sse("done", {
                "session_id": body.session_id,
                "title": session.title,
            })

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control":     "no-cache",
            "X-Accel-Buffering": "no",
        },
    )