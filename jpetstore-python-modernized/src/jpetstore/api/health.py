"""Health check endpoints."""

from fastapi import APIRouter, Request, status
from fastapi.responses import JSONResponse

from jpetstore.core.database import check_database_connection

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_live(request: Request) -> dict[str, str]:
    return {"status": "ok", "request_id": request.state.request_id}


@router.get("/health/ready")
async def health_ready(request: Request) -> JSONResponse:
    db_ok = check_database_connection()
    payload = {
        "status": "ready" if db_ok else "not_ready",
        "database": "up" if db_ok else "down",
        "request_id": request.state.request_id,
    }
    code = status.HTTP_200_OK if db_ok else status.HTTP_503_SERVICE_UNAVAILABLE
    return JSONResponse(status_code=code, content=payload)
