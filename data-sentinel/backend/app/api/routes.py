from fastapi import APIRouter
from backend.app.services.health import health_check

router = APIRouter()

@router.get("/health")
def health():
    return health_check()