"""Checkout idempotency persistence."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from jpetstore.models.base import Base


class CheckoutIdempotency(Base):
    __tablename__ = "checkout_idempotency"
    __table_args__ = (
        UniqueConstraint("userid", "idempotency_key", name="uq_checkout_idem_user_key"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    userid: Mapped[str] = mapped_column(
        String(80), ForeignKey("account.userid", ondelete="CASCADE"), nullable=False
    )
    idempotency_key: Mapped[str] = mapped_column(String(128), nullable=False)
    request_fingerprint: Mapped[str] = mapped_column(String(64), nullable=False)
    orderid: Mapped[int | None] = mapped_column(Integer, ForeignKey("orders.orderid"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
