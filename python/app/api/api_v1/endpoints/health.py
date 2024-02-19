from fastapi import APIRouter

from app.models import HealthResponse

router = APIRouter()


@router.get("/", response_model=HealthResponse)
def health():
    return HealthResponse(message="healthy")
