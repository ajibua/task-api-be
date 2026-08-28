from fastapi import APIRouter

router = APIRouter(prefix="/public", tags=["public"])


@router.get("/info", status_code=200)
def info():
    return {"message": "Welcome stranger! This info is public."}
