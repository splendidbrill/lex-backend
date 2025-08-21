from typing import Optional
from fastapi import Header, HTTPException


def get_current_user_id(authorization: Optional[str] = Header(default=None), x_user_id: Optional[str] = Header(default=None)) -> str:
    # Expecting: Authorization: Bearer <jwt>
    # In production, validate the JWT against Supabase JWKS. For now, use x-user-id for simplicity
    if x_user_id:
        return x_user_id
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Unauthorized")
    # Minimal stub: do not parse JWT here to avoid adding heavy deps
    token = authorization.split(" ", 1)[1].strip()
    if not token:
        raise HTTPException(status_code=401, detail="Invalid token")
    # As a placeholder, treat token as user id in dev
    return token
