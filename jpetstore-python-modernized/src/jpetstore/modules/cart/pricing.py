"""Decimal helpers for cart pricing."""

from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP

MONEY_QUANT = Decimal("0.01")


def money(value: Decimal | None) -> Decimal | None:
    if value is None:
        return None
    return value.quantize(MONEY_QUANT, rounding=ROUND_HALF_UP)


def line_total(unit_price: Decimal | None, quantity: int) -> Decimal | None:
    if unit_price is None:
        return None
    return money(unit_price * quantity)


def sum_lines(totals: list[Decimal | None]) -> Decimal:
    sub = Decimal("0")
    for amount in totals:
        if amount is not None:
            sub += amount
    return money(sub) or Decimal("0.00")
