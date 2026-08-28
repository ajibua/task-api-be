from typing import Optional

from pydantic import BaseModel


class SignUpRequest(BaseModel):
    """Deliberately untyped-strict (plain str, not EmailStr): we want a
    missing/empty field to fall through to our own 400 check in the route,
    not to FastAPI's automatic 422. The server validates, not the schema."""

    email: Optional[str] = None
    password: Optional[str] = None


class LoginRequest(BaseModel):
    email: Optional[str] = None
    password: Optional[str] = None
