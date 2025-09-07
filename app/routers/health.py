from fastapi import APIRouter

router= APIRouter(prefix="/health", tags=["healt"])

@router.get("")
def healthcheck():
    return {"status": "ok"}

