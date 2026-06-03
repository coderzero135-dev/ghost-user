import bcrypt as _bcrypt
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from config import JWT_SECRET, JWT_ALGORITHM, JWT_EXPIRE_HOURS
from database import get_db
from models import User

security = HTTPBearer(auto_error=False)

def hash_password(password: str) -> str:
    pw = password.encode()[:72]
    return _bcrypt.hashpw(pw, _bcrypt.gensalt()).decode()

def verify_password(password: str, hashed: str) -> bool:
    try:
        return _bcrypt.checkpw(password.encode()[:72], hashed.encode())
    except:
        return False

def create_token(user_id: int) -> str:
    payload = {
        "sub": str(user_id),
        "exp": datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRE_HOURS),
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def decode_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except JWTError:
        return None

async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User | None:
    if not credentials:
        return None
    payload = decode_token(credentials.credentials)
    if not payload:
        return None
    user_id = int(payload.get("sub", 0))
    if not user_id:
        return None
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()

async def require_user(user: User | None = Depends(get_current_user)) -> User:
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user
