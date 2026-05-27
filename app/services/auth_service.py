from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import security
from app.repositories import UserRepository
from app.schemas import RegisterRequest, LoginRequest, TokenResponse, UserOut


class AuthService:

    def __init__(self, db: AsyncSession):
        self.repo = UserRepository(db)

    async def register(self, data: RegisterRequest) -> TokenResponse:
        existing = await self.repo.get_by_email(data.email)
        if existing:
            raise HTTPException(409, "Email already registered")
        hashed = security.hash_password(data.password)
        user   = await self.repo.create(data.name, data.email, hashed)
        token  = security.make_token(user.id, user.email, user.role)
        return TokenResponse(
            access_token=token,
            user=UserOut.model_validate(user),
        )

    async def login(self, data: LoginRequest) -> TokenResponse:
        user = await self.repo.get_by_email(data.email)
        if not user or not security.verify_password(
                data.password, user.hashed_password):
            raise HTTPException(401, "Invalid email or password")
        if not user.is_active:
            raise HTTPException(403, "Account is inactive")
        token = security.make_token(user.id, user.email, user.role)
        return TokenResponse(
            access_token=token,
            user=UserOut.model_validate(user),
        )
