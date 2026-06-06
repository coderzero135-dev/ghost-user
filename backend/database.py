from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from backend.config import DATABASE_URL

engine = create_async_engine(DATABASE_URL, echo=False)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

async def get_db():
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise

async def _seed_admin():
    from sqlalchemy import select
    from backend.models import User
    from backend.services.auth import hash_password
    import os
    admin_email = os.getenv("ADMIN_EMAIL", "admin@nipx.app")
    admin_pass = os.getenv("ADMIN_PASSWORD", "nipxadmin123")
    async with async_session() as db:
        result = await db.execute(select(User).where(User.email == admin_email))
        if not result.scalar_one_or_none():
            db.add(User(email=admin_email, password_hash=hash_password(admin_pass), credits=99, is_admin=1))
            await db.commit()

async def init_db():
    async with engine.begin() as conn:
        from backend.models import User, Test, PersonaResult, Issue, UXScore
        await conn.run_sync(Base.metadata.create_all)
    await _seed_admin()
