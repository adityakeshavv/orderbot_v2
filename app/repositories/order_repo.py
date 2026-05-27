from datetime import datetime
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Order, OrderRequest


class OrderRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, order_id: int) -> Optional[Order]:
        result = await self.db.execute(
            select(Order).where(Order.id == order_id)
        )
        return result.scalar_one_or_none()

    async def get_by_customer(self, customer_id: int) -> list[Order]:
        result = await self.db.execute(
            select(Order)
            .where(Order.customer_id == customer_id)
            .order_by(Order.created_at.desc())
        )
        return list(result.scalars().all())

    async def create(self, customer_id: int, product: str,
                     quantity: int, delivery_date: datetime) -> Order:
        order = Order(
            customer_id=customer_id,
            product=product,
            quantity=quantity,
            delivery_date=delivery_date,
            status="Processing",
        )
        self.db.add(order)
        await self.db.flush()
        await self.db.refresh(order)
        return order

    async def cancel(self, order: Order) -> Order:
        order.status = "Closed"
        await self.db.flush()
        await self.db.refresh(order)
        return order

    async def create_request(self, order_id: int,
                              req_type: str, reason: str) -> OrderRequest:
        req = OrderRequest(order_id=order_id, type=req_type, reason=reason)
        self.db.add(req)
        await self.db.flush()
        await self.db.refresh(req)
        return req
