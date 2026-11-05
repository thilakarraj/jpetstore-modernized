"""Account domain service."""

from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from jpetstore.core.exceptions import AppError
from jpetstore.models import Account, Profile
from jpetstore.modules.account.repository import AccountRepository
from jpetstore.modules.account.schemas import (
    AccountProfileResponse,
    AccountUpdateRequest,
    RegisterRequest,
    RegisterResponse,
    TokenResponse,
)
from jpetstore.config import Settings
from jpetstore.modules.account.security import create_access_token
from jpetstore.security.passwords import hash_password, verify_password


@dataclass(frozen=True)
class AuthUser:
    username: str


class AccountService:
    def __init__(self, session: Session) -> None:
        self._session = session
        self._repo = AccountRepository(session)

    def register(self, payload: RegisterRequest) -> RegisterResponse:
        if self._repo.username_exists(payload.username):
            raise AppError(
                code="USERNAME_EXISTS",
                message="Username already exists.",
                status_code=409,
            )
        password_hash = hash_password(payload.password)
        account = Account(
            userid=payload.username,
            email=str(payload.email),
            firstname=payload.first_name,
            lastname=payload.last_name,
            status="OK",
            addr1=payload.address1,
            addr2=payload.address2,
            city=payload.city,
            state=payload.state,
            zip=payload.zip,
            country=payload.country,
            phone=payload.phone,
        )
        profile = Profile(
            userid=payload.username,
            langpref=payload.language_preference,
            favcategory=payload.favourite_category_id,
            mylistopt=1 if payload.list_option else 0,
            banneropt=1 if payload.banner_option else 0,
        )
        try:
            self._repo.add_registration(
                username=payload.username,
                password_hash=password_hash,
                account=account,
                profile=profile,
            )
            self._session.commit()
        except IntegrityError as exc:
            self._session.rollback()
            raise AppError(
                code="USERNAME_EXISTS",
                message="Username already exists.",
                status_code=409,
            ) from exc
        except Exception:
            self._session.rollback()
            raise
        return RegisterResponse(username=payload.username)

    def login(self, username: str, password: str, settings: Settings) -> TokenResponse:
        signon = self._repo.get_signon(username)
        if signon is None or not verify_password(password, signon.password):
            raise AppError(
                code="INVALID_CREDENTIALS",
                message="Invalid username or password. Signon failed.",
                status_code=401,
            )
        token, expires_in = create_access_token(username, settings)
        return TokenResponse(access_token=token, expires_in=expires_in)

    def get_profile(self, user: AuthUser) -> AccountProfileResponse:
        account = self._repo.get_account(user.username)
        profile = self._repo.get_profile(user.username)
        if account is None or profile is None:
            raise AppError(
                code="ACCOUNT_NOT_FOUND",
                message="Account not found.",
                status_code=404,
            )
        return self._to_response(account, profile)

    def update_profile(self, user: AuthUser, payload: AccountUpdateRequest) -> AccountProfileResponse:
        account = self._repo.get_account(user.username)
        profile = self._repo.get_profile(user.username)
        if account is None or profile is None:
            raise AppError(
                code="ACCOUNT_NOT_FOUND",
                message="Account not found.",
                status_code=404,
            )
        if payload.email is not None:
            account.email = str(payload.email)
        if payload.first_name is not None:
            account.firstname = payload.first_name
        if payload.last_name is not None:
            account.lastname = payload.last_name
        if payload.address1 is not None:
            account.addr1 = payload.address1
        if payload.address2 is not None:
            account.addr2 = payload.address2
        if payload.city is not None:
            account.city = payload.city
        if payload.state is not None:
            account.state = payload.state
        if payload.zip is not None:
            account.zip = payload.zip
        if payload.country is not None:
            account.country = payload.country
        if payload.phone is not None:
            account.phone = payload.phone
        if payload.language_preference is not None:
            profile.langpref = payload.language_preference
        if payload.favourite_category_id is not None:
            profile.favcategory = payload.favourite_category_id
        if payload.list_option is not None:
            profile.mylistopt = 1 if payload.list_option else 0
        if payload.banner_option is not None:
            profile.banneropt = 1 if payload.banner_option else 0
        if payload.password is not None:
            signon = self._repo.get_signon(user.username)
            if signon is None:
                raise AppError(
                    code="ACCOUNT_NOT_FOUND",
                    message="Account not found.",
                    status_code=404,
                )
            signon.password = hash_password(payload.password)
        try:
            self._session.commit()
        except Exception:
            self._session.rollback()
            raise
        return self._to_response(account, profile)

    def _to_response(self, account: Account, profile: Profile) -> AccountProfileResponse:
        banner_name = self._repo.get_banner_name(profile.favcategory)
        return AccountProfileResponse(
            username=account.userid,
            email=account.email,
            first_name=account.firstname,
            last_name=account.lastname,
            status=account.status,
            address1=account.addr1,
            address2=account.addr2,
            city=account.city,
            state=account.state,
            zip=account.zip,
            country=account.country,
            phone=account.phone,
            language_preference=profile.langpref,
            favourite_category_id=profile.favcategory,
            list_option=bool(profile.mylistopt) if profile.mylistopt is not None else None,
            banner_option=bool(profile.banneropt) if profile.banneropt is not None else None,
            banner_name=banner_name,
        )
