"""Order module dependencies."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from jpetstore.core.database import get_db_session
from jpetstore.modules.order.service import OrderService

DbSession = Annotated[Session, Depends(get_db_session)]


def get_order_service(session: DbSession) -> OrderService:
    return OrderService(session)


OrderServiceDep = Annotated[OrderService, Depends(get_order_service)]
