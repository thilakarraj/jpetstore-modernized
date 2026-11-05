"""Application-wide exception types and handlers."""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from jpetstore.logging_setup import get_logger

logger = get_logger("exceptions")


class AppError(Exception):
    """Base application error with HTTP mapping."""

    def __init__(self, code: str, message: str, status_code: int = 400) -> None:
        self.code = code
        self.message = message
        self.status_code = status_code
        super().__init__(message)


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
        request_id = getattr(request.state, "request_id", None)
        logger.warning(
            "Business exception",
            extra={
                "request_id": request_id,
                "route": request.url.path,
                "event": "business.exception",
            },
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {"code": exc.code, "message": exc.message},
                "request_id": request_id,
            },
        )

    @app.exception_handler(Exception)
    async def unhandled_error_handler(request: Request, exc: Exception) -> JSONResponse:
        request_id = getattr(request.state, "request_id", None)
        logger.exception(
            "Unhandled exception",
            extra={"request_id": request_id, "route": request.url.path},
        )
        return JSONResponse(
            status_code=500,
            content={
                "error": {"code": "INTERNAL_ERROR", "message": "An unexpected error occurred."},
                "request_id": request_id,
            },
        )
