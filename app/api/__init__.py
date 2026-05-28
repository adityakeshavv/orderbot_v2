from fastapi import APIRouter
from .auth        import router as auth_router
from .sessions    import router as sessions_router
from .chat        import router as chat_router
from .orders      import router as orders_router
from .google_auth import router as google_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(sessions_router)
api_router.include_router(chat_router)
api_router.include_router(orders_router)
api_router.include_router(google_router)

__all__ = ["api_router"]