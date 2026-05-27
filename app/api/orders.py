from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models import User
from app.repositories import OrderRepository, UserRepository

router = APIRouter(prefix="/orders", tags=["orders"])


@router.get("")
async def my_orders(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    user_repo  = UserRepository(db)
    customer   = await user_repo.get_customer_by_user_id(current_user.id)
    if not customer:
        return []
    order_repo = OrderRepository(db)
    orders     = await order_repo.get_by_customer(customer.id)
    return [
        {
            "id":            o.id,
            "product":       o.product,
            "quantity":      o.quantity,
            "status":        o.status,
            "delivery_date": o.delivery_date.isoformat()
                             if o.delivery_date else None,
            "created_at":    o.created_at.isoformat(),
        }
        for o in orders
    ]
