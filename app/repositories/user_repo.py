from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Customer, User


class UserRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_email(self, email: str) -> Optional[User]:
        result = await self.db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()

    async def get_by_id(self, user_id: int) -> Optional[User]:
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def create(self, name: str, email: str,
                     hashed_password: str) -> User:
        user = User(name=name, email=email,
                    hashed_password=hashed_password)
        self.db.add(user)
        await self.db.flush()   # get user.id without committing
        # auto-create customer profile
        customer = Customer(user_id=user.id, name=name, email=email)
        self.db.add(customer)
        await self.db.flush()
        await self.db.refresh(user)
        return user

    async def get_customer_by_user_id(
            self, user_id: int) -> Optional[Customer]:
        result = await self.db.execute(
            select(Customer).where(Customer.user_id == user_id)
        )
        return result.scalar_one_or_none()
