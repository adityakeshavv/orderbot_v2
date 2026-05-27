"""
Async seed script.
Run from project root: python seed.py
"""
import asyncio
from datetime import datetime, timedelta, timezone

from app.core.config import settings
from app.core.database import AsyncSessionLocal, create_all_tables
from app.core.security import security
from app.models import User, Customer, Order


async def seed():
    await create_all_tables()

    async with AsyncSessionLocal() as db:
        # Check if already seeded
        from sqlalchemy import select
        result = await db.execute(select(User).limit(1))
        if result.scalar_one_or_none():
            print("Already seeded.")
            return

        # Create users + customers
        users_data = [
            ("Rajesh Kumar", "rajesh@tatasteel.in"),
            ("Anita Singh",  "anita@tatasteel.in"),
            ("Suresh Patel", "suresh@tatasteel.in"),
        ]

        users = []
        for name, email in users_data:
            user = User(
                name=name,
                email=email,
                hashed_password=security.hash_password("Test1234"),
            )
            db.add(user)
            await db.flush()

            customer = Customer(
                user_id=user.id, name=name, email=email)
            db.add(customer)
            await db.flush()
            users.append((user, customer))

        # Create sample orders
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        orders_data = [
            ("Cold Rolled Steel Sheets", "Processing",  10, 500),
            ("Hot Rolled Steel Coils",   "Shipped",      3, 200),
            ("Galvanized Steel Sheets",  "Delivered",   -2, 150),
            ("Steel Pipes",              "Processing",  14,  75),
            ("Structural Steel Beams",   "Closed",     -20, 300),
        ]

        for i, (product, status, days, qty) in enumerate(orders_data):
            _, customer = users[i % len(users)]
            order = Order(
                customer_id=customer.id,
                product=product,
                quantity=qty,
                delivery_date=now + timedelta(days=days),
                status=status,
            )
            db.add(order)

        await db.commit()

        print("✅ Seeded successfully!")
        print("\nDemo accounts (password: Test1234):")
        for _, (name, email) in enumerate(users_data):
            print(f"  {email}")


if __name__ == "__main__":
    asyncio.run(seed())
