from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.supabase_client import supabase

# auto_error=False so a missing header falls through to our own 401 JSON
# (via the app's HTTPException handler) instead of FastAPI's default body.
# Using HTTPBearer (not a raw Header) is what makes the padlock/"Authorize"
# button appear on protected routes in Swagger UI at /docs.
bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
):
    """The one guard, reused by every protected route.

    - No/malformed Authorization header -> 401 "Access token required"
    - Header present but Supabase rejects the token -> 401 "Invalid or
      expired token"
    - Otherwise -> returns the verified Supabase user object, available to
      the route as `current_user`.
    """
    if credentials is None or not credentials.credentials:
        raise HTTPException(status_code=401, detail="Access token required")

    token = credentials.credentials

    try:
        response = supabase.auth.get_user(token)
    except Exception:
        # Supabase raises for a tampered, malformed, or expired token.
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user = getattr(response, "user", None)
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    return user
