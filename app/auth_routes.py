from fastapi import APIRouter, Depends, HTTPException, Response

from app.auth_schemas import LoginRequest, SignUpRequest
from app.dependencies import get_current_user
from app.supabase_client import supabase

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", status_code=201)
def signup(payload: SignUpRequest):
    """Create a new user account via Supabase Auth. The server never
    stores or hashes the password itself -- it only forwards it."""
    if not payload.email or not payload.password:
        raise HTTPException(status_code=400, detail="Email and password are required")

    try:
        result = supabase.auth.sign_up(
            {"email": payload.email, "password": payload.password}
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    if result.user is None:
        raise HTTPException(status_code=400, detail="Could not create user")

    return {
        "id": result.user.id,
        "email": result.user.email,
        "created_at": result.user.created_at,
    }


@router.post("/login", status_code=200)
def login(payload: LoginRequest):
    """Authenticate against Supabase and hand back its access + refresh
    tokens. The access token is what callers put in the Authorization
    header on every later request."""
    if not payload.email or not payload.password:
        raise HTTPException(status_code=400, detail="Email and password are required")

    try:
        result = supabase.auth.sign_in_with_password(
            {"email": payload.email, "password": payload.password}
        )
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid login credentials")

    if result.session is None:
        raise HTTPException(status_code=401, detail="Invalid login credentials")

    return {
        "access_token": result.session.access_token,
        "refresh_token": result.session.refresh_token,
        "token_type": "bearer",
    }


@router.post("/logout", status_code=204)
def logout(current_user=Depends(get_current_user)):
    """Protected by the same guard as /protected/* routes: you must
    present a valid token to end its session."""
    try:
        supabase.auth.sign_out()
    except Exception:
        # Sign-out failing server-side shouldn't block the client from
        # discarding its token; either way the caller is done with it.
        pass
    return Response(status_code=204)
