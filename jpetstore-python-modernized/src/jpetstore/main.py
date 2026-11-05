"""FastAPI application factory."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from jpetstore.api.health import router as health_router
from jpetstore.api.metrics import router as metrics_router
from jpetstore.config import Settings, get_settings
from jpetstore.core.database import dispose_database, init_database
from jpetstore.core.exceptions import register_exception_handlers
from jpetstore.logging_setup import configure_logging, get_logger, shutdown_logging
from jpetstore.middleware.logging_middleware import RequestLoggingMiddleware
from jpetstore.middleware.metrics_middleware import MetricsMiddleware
from jpetstore.middleware.request_id import RequestIdMiddleware
from jpetstore.middleware.security_headers import SecurityHeadersMiddleware
from jpetstore.modules.account.router import router as account_router
from jpetstore.modules.cart.router import router as cart_router
from jpetstore.modules.catalog.router import router as catalog_router
from jpetstore.modules.order.router import router as order_router

logger = get_logger("main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    configure_logging(settings, enable_stdout=True)
    logger.info("Application startup", extra={"event": "app.startup"})
    try:
        init_database(settings)
    except Exception:
        logger.exception("Database initialization failed", extra={"event": "database.init.failure"})
        raise
    yield
    logger.info("Application shutdown", extra={"event": "app.shutdown"})
    dispose_database()
    shutdown_logging()


def create_app(settings: Settings | None = None) -> FastAPI:
    cfg = settings or get_settings()
    app = FastAPI(
        title="JPetStore API",
        version="0.1.0",
        lifespan=lifespan,
        docs_url="/docs",
        openapi_url="/openapi.json",
    )

    register_exception_handlers(app)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=cfg.cors_origin_list,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "Idempotency-Key", "X-Cart-Id", "X-Request-Id"],
    )
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(MetricsMiddleware)
    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(RequestIdMiddleware)

    app.include_router(health_router)
    app.include_router(metrics_router)
    app.include_router(account_router)
    app.include_router(catalog_router)
    app.include_router(cart_router)
    app.include_router(order_router)

    return app


app = create_app()
