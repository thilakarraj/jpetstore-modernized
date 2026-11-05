"""Cart API schemas."""

from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class AddCartItemRequest(StrictModel):
    item_id: str = Field(min_length=1, max_length=10)
    quantity: int = Field(default=1, ge=1, le=9999)


class UpdateCartItemRequest(StrictModel):
    quantity: int = Field(ge=1, le=9999)


class CartLineResponse(BaseModel):
    item_id: str
    product_id: str | None = None
    product_name: str | None = None
    quantity: int
    list_price: Decimal | None = None
    line_total: Decimal | None = None
    in_stock: bool = False
    item_available: bool = True


class CartResponse(BaseModel):
    cart_id: int
    lines: list[CartLineResponse]
    sub_total: Decimal
