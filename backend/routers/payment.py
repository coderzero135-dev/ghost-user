from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.database import get_db
from backend.services.auth import get_current_user, require_user
from backend.models import User
import hashlib
import hmac
import os
import base64
import httpx

router = APIRouter(prefix="/api/payment", tags=["payment"])

RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID", "")
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET", "")

PLANS = {
    "pro": {"name": "Pro", "price": 99900, "credits": 30},
    "agency": {"name": "Agency", "price": 499900, "credits": 999},
}


@router.get("/config")
async def payment_config(user: User = Depends(require_user)):
    return {
        "key_id": RAZORPAY_KEY_ID,
        "plans": PLANS,
    }


class CreateOrderRequest(BaseModel):
    plan: str


@router.post("/create-order")
async def create_order(req: CreateOrderRequest, user: User = Depends(require_user)):
    if not RAZORPAY_KEY_ID or not RAZORPAY_KEY_SECRET:
        raise HTTPException(status_code=400, detail="Payment not configured")

    plan = PLANS.get(req.plan)
    if not plan:
        raise HTTPException(status_code=400, detail="Invalid plan")

    import httpx
    auth = f"{RAZORPAY_KEY_ID}:{RAZORPAY_KEY_SECRET}"
    import base64
    encoded = base64.b64encode(auth.encode()).decode()

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(
            "https://api.razorpay.com/v1/orders",
            json={
                "amount": plan["price"],
                "currency": "INR",
                "receipt": f"nipx_{user.id}_{req.plan}",
                "notes": {"user_id": str(user.id), "plan": req.plan},
            },
            headers={"Authorization": f"Basic {encoded}"},
        )
        if resp.status_code != 200:
            raise HTTPException(status_code=400, detail=f"Razorpay error: {resp.text[:200]}")
        data = resp.json()
        return {
            "order_id": data["id"],
            "amount": data["amount"],
            "currency": data["currency"],
            "key_id": RAZORPAY_KEY_ID,
            "user_email": user.email,
        }


class VerifyRequest(BaseModel):
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str
    plan: str


@router.post("/verify")
async def verify_payment(req: VerifyRequest, user: User = Depends(require_user), db: AsyncSession = Depends(get_db)):
    if not RAZORPAY_KEY_SECRET:
        raise HTTPException(status_code=400, detail="Payment not configured")

    msg = f"{req.razorpay_order_id}|{req.razorpay_payment_id}"
    expected = hmac.new(
        RAZORPAY_KEY_SECRET.encode(),
        msg.encode(),
        hashlib.sha256,
    ).hexdigest()

    if expected != req.razorpay_signature:
        raise HTTPException(status_code=400, detail="Invalid signature")

    db_user = await db.get(User, user.id)
    if db_user:
        plan = PLANS.get(req.plan)
        if plan:
            db_user.plan = req.plan
            db_user.credits = plan["credits"]
    await db.commit()
    return {"ok": True, "plan": req.plan, "credits": PLANS[req.plan]["credits"]}
