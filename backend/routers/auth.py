from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.database import get_db
from backend.models import User
from backend.services.auth import hash_password, verify_password, create_token, require_user, get_current_user

router = APIRouter(prefix="/api/auth", tags=["auth"])

class SignupRequest(BaseModel):
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

class AuthResponse(BaseModel):
    token: str
    user: dict

@router.post("/signup")
async def signup(req: SignupRequest, db: AsyncSession = Depends(get_db)):
    if len(req.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")
    existing = await db.execute(select(User).where(User.email == req.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(email=req.email, password_hash=hash_password(req.password), credits=3)
    db.add(user)
    await db.flush()
    await db.refresh(user)
    token = create_token(user.id)
    return AuthResponse(token=token, user={"id": user.id, "email": user.email, "credits": user.credits, "is_admin": bool(user.is_admin)})

@router.post("/login")
async def login(req: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == req.email))
    user = result.scalar_one_or_none()
    if not user or not user.password_hash or not verify_password(req.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    token = create_token(user.id)
    return AuthResponse(token=token, user={"id": user.id, "email": user.email, "credits": user.credits, "is_admin": bool(user.is_admin)})

@router.get("/me")
async def get_me(user: User = Depends(require_user)):
    return {"id": user.id, "email": user.email, "credits": user.credits, "is_admin": bool(user.is_admin)}
