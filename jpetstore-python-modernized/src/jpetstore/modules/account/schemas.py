"""Account API request and response schemas."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

ALLOWED_LANGUAGES = frozenset({"english", "japanese"})
ALLOWED_CATEGORIES = frozenset({"FISH", "DOGS", "REPTILES", "CATS", "BIRDS"})


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class RegisterRequest(StrictModel):
    username: str = Field(min_length=1, max_length=25)
    password: str = Field(min_length=1, max_length=72)
    email: EmailStr
    first_name: str = Field(min_length=1, max_length=80)
    last_name: str = Field(min_length=1, max_length=80)
    address1: str = Field(min_length=1, max_length=80)
    address2: str | None = Field(default=None, max_length=80)
    city: str = Field(min_length=1, max_length=80)
    state: str = Field(min_length=1, max_length=80)
    zip: str = Field(min_length=1, max_length=20)
    country: str = Field(min_length=1, max_length=20)
    phone: str = Field(min_length=1, max_length=80)
    language_preference: Literal["english", "japanese"]
    favourite_category_id: Literal["FISH", "DOGS", "REPTILES", "CATS", "BIRDS"]
    list_option: bool = True
    banner_option: bool = True


class RegisterResponse(BaseModel):
    username: str


class LoginRequest(StrictModel):
    username: str = Field(min_length=1, max_length=25)
    password: str = Field(min_length=1, max_length=72)


class TokenResponse(BaseModel):
    access_token: str
    token_type: Literal["bearer"] = "bearer"
    expires_in: int


class AccountProfileResponse(BaseModel):
    username: str
    email: str
    first_name: str
    last_name: str
    status: str | None = None
    address1: str
    address2: str | None = None
    city: str
    state: str
    zip: str
    country: str
    phone: str
    language_preference: str
    favourite_category_id: str | None = None
    list_option: bool | None = None
    banner_option: bool | None = None
    banner_name: str | None = None


class AccountUpdateRequest(StrictModel):
    email: EmailStr | None = None
    first_name: str | None = Field(default=None, min_length=1, max_length=80)
    last_name: str | None = Field(default=None, min_length=1, max_length=80)
    address1: str | None = Field(default=None, min_length=1, max_length=80)
    address2: str | None = Field(default=None, max_length=80)
    city: str | None = Field(default=None, min_length=1, max_length=80)
    state: str | None = Field(default=None, min_length=1, max_length=80)
    zip: str | None = Field(default=None, min_length=1, max_length=20)
    country: str | None = Field(default=None, min_length=1, max_length=20)
    phone: str | None = Field(default=None, min_length=1, max_length=80)
    language_preference: Literal["english", "japanese"] | None = None
    favourite_category_id: Literal["FISH", "DOGS", "REPTILES", "CATS", "BIRDS"] | None = None
    list_option: bool | None = None
    banner_option: bool | None = None
    password: str | None = Field(default=None, min_length=1, max_length=72)

    @field_validator("password")
    @classmethod
    def reject_blank_password(cls, value: str | None) -> str | None:
        if value is not None and not value.strip():
            raise ValueError("password must not be empty when provided")
        return value
