from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories import OrderRepository
from app.services.email_service import email_service
from .base import ToolResult


class OrderTools:
    """
    All tools the LLM agent can call.
    Each method is async, returns a ToolResult.
    Never touches the conversation — only the database and email.
    """

    def __init__(self, db: AsyncSession, customer_id: int):
        self.db          = db
        self.customer_id = customer_id
        self.repo        = OrderRepository(db)

    async def get_order(self, order_id: int) -> ToolResult:
        order = await self.repo.get_by_id(order_id)
        if not order:
            return ToolResult(False, error=f"Order #{order_id} not found.")
        if order.customer_id != self.customer_id:
            return ToolResult(
                False,
                error=f"You don't have access to Order #{order_id}."
            )
        return ToolResult(True, data={
            "id":            order.id,
            "product":       order.product,
            "quantity":      order.quantity,
            "status":        order.status,
            "delivery_date": order.delivery_date.strftime("%d %b %Y")
                             if order.delivery_date else "TBD",
        })

    async def list_orders(self) -> ToolResult:
        orders = await self.repo.get_by_customer(self.customer_id)
        return ToolResult(True, data=[
            {
                "id":            o.id,
                "product":       o.product,
                "quantity":      o.quantity,
                "status":        o.status,
                "delivery_date": o.delivery_date.strftime("%d %b %Y")
                                 if o.delivery_date else "TBD",
            }
            for o in orders
        ])

    async def place_order(self, product: str, quantity: int,
                           delivery_date: datetime) -> ToolResult:
        if quantity <= 0:
            return ToolResult(False,
                              error="Quantity must be greater than zero.")
        if delivery_date <= datetime.utcnow():
            return ToolResult(False,
                              error="Delivery date must be in the future.")
        order = await self.repo.create(
            self.customer_id, product, quantity, delivery_date)
        return ToolResult(True, data={
            "id":            order.id,
            "product":       order.product,
            "quantity":      order.quantity,
            "status":        order.status,
            "delivery_date": order.delivery_date.strftime("%d %b %Y"),
        })

    async def cancel_order(self, order_id: int) -> ToolResult:
        order = await self.repo.get_by_id(order_id)
        if not order:
            return ToolResult(False, error=f"Order #{order_id} not found.")
        if order.customer_id != self.customer_id:
            return ToolResult(
                False,
                error=f"You don't have access to Order #{order_id}."
            )
        if order.status in ("Delivered", "Closed"):
            return ToolResult(
                False,
                error=f"Order #{order_id} is already {order.status}."
            )
        await self.repo.cancel(order)
        return ToolResult(True, data={
            "id": order_id, "product": order.product})

    async def speed_up_order(self, order_id: int,
                              reason: str) -> ToolResult:
        order = await self.repo.get_by_id(order_id)
        if not order:
            return ToolResult(False, error=f"Order #{order_id} not found.")
        if order.customer_id != self.customer_id:
            return ToolResult(
                False,
                error=f"You don't have access to Order #{order_id}."
            )
        if order.status in ("Delivered", "Closed"):
            return ToolResult(
                False,
                error=f"Order #{order_id} is already {order.status}."
            )
        await self.repo.create_request(order_id, "speed_up", reason)
        await email_service.send(
            subject=f"Speed-Up Request — Order #{order_id}",
            body=(
                f"Order   : #{order_id}\n"
                f"Product : {order.product}\n"
                f"Reason  : {reason}\n"
                f"Time    : {datetime.utcnow().strftime('%d %b %Y %H:%M UTC')}"
            ),
        )
        return ToolResult(True, data={
            "order_id": order_id, "product": order.product})

    async def swap_order(self, order_id: int,
                          details: str) -> ToolResult:
        order = await self.repo.get_by_id(order_id)
        if not order:
            return ToolResult(False, error=f"Order #{order_id} not found.")
        if order.customer_id != self.customer_id:
            return ToolResult(
                False,
                error=f"You don't have access to Order #{order_id}."
            )
        if order.status in ("Delivered", "Closed"):
            return ToolResult(
                False,
                error=f"Order #{order_id} is already {order.status}."
            )
        await self.repo.create_request(order_id, "swap", details)
        await email_service.send(
            subject=f"Swap Request — Order #{order_id}",
            body=(
                f"Order   : #{order_id}\n"
                f"Product : {order.product}\n"
                f"Details : {details}\n"
                f"Time    : {datetime.utcnow().strftime('%d %b %Y %H:%M UTC')}"
            ),
        )
        return ToolResult(True, data={
            "order_id": order_id, "product": order.product})
