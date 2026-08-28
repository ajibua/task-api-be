from fastapi import APIRouter, Depends

from app.dependencies import get_current_user

router = APIRouter(prefix="/protected", tags=["protected"])


@router.get("/profile", status_code=200)
def profile(current_user=Depends(get_current_user)):
    """Only reachable with a valid access token. `current_user` is the
    object get_current_user attached after verifying the token."""
    return {
        "id": current_user.id,
        "email": current_user.email,
        "created_at": current_user.created_at,
    }


@router.get("/dashboard", status_code=200)
def dashboard(current_user=Depends(get_current_user)):
    """A second protected route, added to prove the guard is reusable:
    no new auth code, just Depends(get_current_user) again."""
    return {"message": f"Welcome to your dashboard, {current_user.email}."}
