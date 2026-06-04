import asyncio, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

async def main():
    from backend.database import async_session
    from backend.models import User
    from sqlalchemy import select
    async with async_session() as db:
        email = input("Email to make admin: ").strip()
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        if user:
            user.is_admin = 1
            await db.commit()
            print(f"\n{email} is now admin. Visit /admin")
        else:
            print("\nUser not found. Sign up first, then run this again.")

asyncio.run(main())
