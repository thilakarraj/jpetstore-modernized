"""FastAPI dependencies for catalog routes."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from jpetstore.config import Settings, get_settings
from jpetstore.core.database import get_db_session
from jpetstore.modules.catalog.service import CatalogService

DbSession = Annotated[Session, Depends(get_db_session)]
AppSettings = Annotated[Settings, Depends(get_settings)]


def get_catalog_service(session: DbSession, settings: AppSettings) -> CatalogService:
    return CatalogService(session, settings)


CatalogServiceDep = Annotated[CatalogService, Depends(get_catalog_service)]
