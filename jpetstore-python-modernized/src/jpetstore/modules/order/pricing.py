"""Order pricing helpers."""

from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP

from jpetstore.modules.cart.pricing import MONEY_QUANT, money


def order_line_total(unit_price: Decimal, quantity: int) -> Decimal:
    return money(unit_price * quantity) or Decimal("0.00")


def mask_card_last_four(last_four: str) -> str:
    return f"****{last_four}"


def mask_card_for_response(stored: str) -> str:
    if stored.startswith("****"):
        return stored
    digits = "".join(ch for ch in stored if ch.isdigit())
    if len(digits) >= 4:
        return f"****{digits[-4:]}"
    return "****"
