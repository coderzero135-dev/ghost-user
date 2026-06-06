import hashlib
import hmac
import os
import httpx
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from backend.database import get_db
from backend.models import User
from backend.services.auth import require_user

router = APIRouter(prefix="/api/payment", tags=["payment"])

RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID", "")
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET", "")

PLANS = {
    "pro": {"name": "Pro", "amount": 99900, "credits": 30, "price_label": "₹999"},
    "agency": {"name": "Agency", "amount": 499900, "credits": 999, "price_label": "₹4,999"},
}


@router.get("/config")
async def config(user: User = Depends(require_user)):
    return {"key_id": RAZORPAY_KEY_ID, "currency": "INR", "plans": PLANS}


class CreateOrder(BaseModel):
    plan: str


@router.post("/create-order")
async def create_order(req: CreateOrder, user: User = Depends(require_user)):
    if not RAZORPAY_KEY_ID:
        raise HTTPException(400, "Razorpay not configured")
    plan = PLANS.get(req.plan)
    if not plan:
        raise HTTPException(400, "Invalid plan")

    import base64
    auth = base64.b64encode(f"{RAZORPAY_KEY_ID}:{RAZORPAY_KEY_SECRET}".encode()).decode()
    async with httpx.AsyncClient(timeout=30) as c:
        r = await c.post(
            "https://api.razorpay.com/v1/orders",
            json={"amount": plan["amount"], "currency": "INR", "receipt": f"nipx_{user.id}_{req.plan}",
                  "notes": {"user_id": str(user.id), "plan": req.plan}},
            headers={"Authorization": f"Basic {auth}"},
        )
        if r.status_code != 200:
            raise HTTPException(400, f"Razorpay: {r.text[:200]}")
        data = r.json()
        return {"order_id": data["id"], "amount": data["amount"], "key_id": RAZORPAY_KEY_ID, "prefill_email": user.email}


class VerifyPayment(BaseModel):
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str
    plan: str


@router.post("/verify")
async def verify(req: VerifyPayment, user: User = Depends(require_user), db: AsyncSession = Depends(get_db)):
    plan = PLANS.get(req.plan)
    if not plan:
        raise HTTPException(400, "Invalid plan")

    msg = f"{req.razorpay_order_id}|{req.razorpay_payment_id}"
    expected = hmac.new(RAZORPAY_KEY_SECRET.encode(), msg.encode(), hashlib.sha256).hexdigest()
    if expected != req.razorpay_signature:
        raise HTTPException(400, "Invalid payment signature")

    db_user = await db.get(User, user.id)
    if db_user:
        db_user.plan = req.plan
        db_user.credits = plan["credits"]
    await db.commit()
    return {"ok": True, "plan": req.plan, "credits": plan["credits"]}
