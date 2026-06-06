from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.database import get_db
from backend.models import User, Test
from backend.services.auth import get_current_user

router = APIRouter(prefix="/api/admin", tags=["admin"])

class UserUpdate(BaseModel):
    credits: int | None = None
    plan: str | None = None
    is_admin: bool | None = None


async def require_admin(user: User = Depends(get_current_user)):
    if not user or not user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    return user


class SetupRequest(BaseModel):
    email: str
    secret: str = ""


@router.post("/setup")
async def setup_admin(req: SetupRequest, db: AsyncSession = Depends(get_db)):
    if req.secret != "admin123":
        raise HTTPException(status_code=403, detail="Invalid secret")
    result = await db.execute(select(User).where(User.email == req.email))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found - sign up first")
    user.is_admin = 1
    await db.commit()
    return {"ok": True, "message": f"{req.email} is now admin"}


@router.get("/force-setup")
async def force_setup(email: str, password: str = "", secret: str = "", db: AsyncSession = Depends(get_db)):
    if secret != "admin123":
        raise HTTPException(status_code=403, detail="Invalid secret")
    from backend.services.auth import hash_password
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if not user:
        user = User(email=email, password_hash=hash_password(password or "nipxadmin123"), credits=99, is_admin=1, plan="pro")
        db.add(user)
    else:
        user.is_admin = 1
    await db.commit()
    return {"ok": True, "email": email, "message": "Admin ready", "password": password or "nipxadmin123"}


@router.get("/stats")
async def admin_stats(db: AsyncSession = Depends(get_db), _: User = Depends(require_admin)):
    users_result = await db.execute(select(User))
    users = users_result.scalars().all()
    tests_result = await db.execute(select(Test))
    tests = tests_result.scalars().all()
    return {
        "total_users": len(users),
        "total_tests": len(tests),
        "completed_tests": len([t for t in tests if t.status == "completed"]),
        "failed_tests": len([t for t in tests if t.status == "failed"]),
        "premium_users": len([u for u in users if u.plan and u.plan != "free"]),
    }


@router.get("/users")
async def list_users(db: AsyncSession = Depends(get_db), _: User = Depends(require_admin)):
    result = await db.execute(select(User).order_by(User.created_at.desc()))
    users = result.scalars().all()
    return [{
        "id": u.id, "email": u.email, "credits": u.credits,
        "plan": u.plan or "free", "is_admin": bool(u.is_admin),
        "created_at": u.created_at.isoformat() if u.created_at else None,
    } for u in users]


@router.put("/users/{user_id}")
async def update_user(user_id: int, payload: UserUpdate, db: AsyncSession = Depends(get_db), _: User = Depends(require_admin)):
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if payload.credits is not None:
        user.credits = payload.credits
    if payload.plan is not None:
        user.plan = payload.plan
    if payload.is_admin is not None:
        user.is_admin = 1 if payload.is_admin else 0
    await db.commit()
    return {"ok": True}
