import os
import httpx
from fastapi import APIRouter, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from authlib.integrations.httpx_client import AsyncOAuth2Client

from app.core.database import get_db
from app.core.security import security
from app.repositories import UserRepository

router = APIRouter(prefix="/auth", tags=["auth"])

GOOGLE_CLIENT_ID     = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI  = os.getenv("GOOGLE_REDIRECT_URI")
GOOGLE_AUTH_URL      = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL     = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL  = "https://www.googleapis.com/oauth2/v3/userinfo"


@router.get("/google")
async def google_login():
    """Redirect user to Google consent screen."""
    params = {
        "client_id":     GOOGLE_CLIENT_ID,
        "redirect_uri":  GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope":         "openid email profile",
        "access_type":   "offline",
    }
    from urllib.parse import urlencode
    url = f"{GOOGLE_AUTH_URL}?{urlencode(params)}"
    return RedirectResponse(url)


@router.get("/google/callback")
async def google_callback(
    code: str,
    db: AsyncSession = Depends(get_db),
):
    """Handle Google OAuth callback — create or login user."""
    async with httpx.AsyncClient() as client:
        # Exchange code for token
        token_resp = await client.post(GOOGLE_TOKEN_URL, data={
            "code":          code,
            "client_id":     GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "redirect_uri":  GOOGLE_REDIRECT_URI,
            "grant_type":    "authorization_code",
        })
        token_data = token_resp.json()

        # Get user info
        userinfo_resp = await client.get(
            GOOGLE_USERINFO_URL,
            headers={"Authorization": f"Bearer {token_data['access_token']}"},
        )
        userinfo = userinfo_resp.json()

    email = userinfo["email"]
    name  = userinfo.get("name", email.split("@")[0])

    # Create or get user
    repo = UserRepository(db)
    user = await repo.get_by_email(email)
    if not user:
        user = await repo.create(
            name, email,
            security.hash_password(os.urandom(32).hex())
        )

    token = security.make_token(user.id, user.email, user.role)

    # Redirect to frontend with token
    frontend = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")
    return RedirectResponse(
        f"{frontend}/auth/callback?token={token}"
            f"&name={name}&email={email}&role={user.role}"
    )