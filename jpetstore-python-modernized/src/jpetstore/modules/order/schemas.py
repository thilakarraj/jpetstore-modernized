"""Order and checkout API schemas."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

ALLOWED_CARD_TYPES = frozenset({"Visa", "MasterCard", "American Express"})


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class CheckoutRequest(StrictModel):
    ship_to_first_name: str = Field(min_length=1, max_length=80)
    ship_to_last_name: str = Field(min_length=1, max_length=80)
    ship_address1: str = Field(min_length=1, max_length=80)
    ship_address2: str | None = Field(default=None, max_length=80)
    ship_city: str = Field(min_length=1, max_length=80)
    ship_state: str = Field(min_length=1, max_length=80)
    ship_zip: str = Field(min_length=1, max_length=20)
    ship_country: str = Field(min_length=1, max_length=20)
    bill_to_first_name: str = Field(min_length=1, max_length=80)
    bill_to_last_name: str = Field(min_length=1, max_length=80)
    bill_address1: str = Field(min_length=1, max_length=80)
    bill_address2: str | None = Field(default=None, max_length=80)
    bill_city: str = Field(min_length=1, max_length=80)
    bill_state: str = Field(min_length=1, max_length=80)
    bill_zip: str = Field(min_length=1, max_length=20)
    bill_country: str = Field(min_length=1, max_length=20)
    courier: str = Field(min_length=1, max_length=80)
    locale: str = Field(min_length=1, max_length=80)
    card_type: Literal["Visa", "MasterCard", "American Express"]
    card_last_four: str = Field(min_length=4, max_length=4, pattern=r"^\d{4}$")
    expiry_date: str = Field(min_length=4, max_length=7)


class OrderLineResponse(BaseModel):
    line_number: int
    item_id: str
    quantity: int
    unit_price: Decimal
    line_total: Decimal


class OrderSummaryResponse(BaseModel):
    order_id: int
    order_date: date
    total_price: Decimal
    status: str


class OrderListResponse(BaseModel):
    orders: list[OrderSummaryResponse]


class OrderDetailResponse(BaseModel):
    order_id: int
    order_date: date
    total_price: Decimal
    status: str
    courier: str
    locale: str
    card_type: str
    card_display: str
    expiry_date: str
    ship_to_first_name: str
    ship_to_last_name: str
    ship_address1: str
    ship_address2: str | None
    ship_city: str
    ship_state: str
    ship_zip: str
    ship_country: str
    bill_to_first_name: str
    bill_to_last_name: str
    bill_address1: str
    bill_address2: str | None
    bill_city: str
    bill_state: str
    bill_zip: str
    bill_country: str
    lines: list[OrderLineResponse]


class CheckoutResponse(BaseModel):
    order_id: int
    message: str = "Thank you, your order has been submitted."
    order: OrderDetailResponse
    idempotent_replay: bool = False
