"""Cart route dependencies."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from jpetstore.core.database import get_db_session
from jpetstore.modules.cart.service import CartService

DbSession = Annotated[Session, Depends(get_db_session)]


def get_cart_service(session: DbSession) -> CartService:
    return CartService(session)


CartServiceDep = Annotated[CartService, Depends(get_cart_service)]
