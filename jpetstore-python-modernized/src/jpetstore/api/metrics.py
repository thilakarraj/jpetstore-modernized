"""Prometheus /metrics endpoint."""

import secrets
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import Response
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from jpetstore.config import Settings, get_settings

router = APIRouter(tags=["metrics"])
_basic = HTTPBasic(auto_error=False)


def _verify_metrics_auth(
    credentials: Annotated[HTTPBasicCredentials | None, Depends(_basic)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> None:
    if not settings.metrics_protect:
        return
    if credentials is None:
        raise HTTPException(status_code=401, detail="Unauthorized", headers={"WWW-Authenticate": "Basic"})
    user_ok = secrets.compare_digest(credentials.username, settings.metrics_username)
    pass_ok = secrets.compare_digest(credentials.password, settings.metrics_password)
    if not (user_ok and pass_ok):
        raise HTTPException(status_code=401, detail="Unauthorized", headers={"WWW-Authenticate": "Basic"})


@router.get("/metrics")
async def metrics(
    request: Request,
    _: Annotated[None, Depends(_verify_metrics_auth)],
) -> Response:
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
