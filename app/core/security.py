from datetime import datetime, timedelta
from typing import Optional

import bcrypt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from .config import settings
from .database import get_db

oauth2 = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)


class SecurityService:

    @staticmethod
    def hash_password(plain: str) -> str:
        return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()

    @staticmethod
    def verify_password(plain: str, hashed: str) -> bool:
        return bcrypt.checkpw(plain.encode(), hashed.encode())

    @staticmethod
    def make_token(user_id: int, email: str, role: str) -> str:
        payload = {
            "sub":   str(user_id),
            "email": email,
            "role":  role,
            "exp":   datetime.utcnow() + timedelta(
                hours=settings.TOKEN_EXPIRY_HOURS),
        }
        return jwt.encode(payload, settings.SECRET_KEY,
                          algorithm=settings.ALGORITHM)

    @staticmethod
    def decode_token(token: str) -> dict:
        try:
            return jwt.decode(token, settings.SECRET_KEY,
                              algorithms=[settings.ALGORITHM])
        except JWTError:
            raise HTTPException(status_code=401,
                                detail="Invalid or expired token")


security = SecurityService()


async def get_current_user(
    token: Optional[str] = Depends(oauth2),
    db: AsyncSession = Depends(get_db),
):
    from app.repositories.user_repo import UserRepository
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    payload = security.decode_token(token)
    repo = UserRepository(db)
    user = await repo.get_by_id(int(payload["sub"]))
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found")
    return user


async def get_current_user_optional(
    token: Optional[str] = Depends(oauth2),
    db: AsyncSession = Depends(get_db),
):
    if not token:
        return None
    try:
        return await get_current_user(token, db)
    except HTTPException:
        return None
