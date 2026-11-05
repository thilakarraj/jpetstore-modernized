"""Account data access."""

from __future__ import annotations

from sqlalchemy.orm import Session

from jpetstore.models import Account, BannerData, Profile, Signon


class AccountRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def username_exists(self, username: str) -> bool:
        account = self._session.get(Account, username)
        if account is not None:
            return True
        signon = self._session.get(Signon, username)
        return signon is not None

    def get_signon(self, username: str) -> Signon | None:
        return self._session.get(Signon, username)

    def get_account(self, username: str) -> Account | None:
        return self._session.get(Account, username)

    def get_profile(self, username: str) -> Profile | None:
        return self._session.get(Profile, username)

    def get_banner_name(self, favcategory: str | None) -> str | None:
        if not favcategory:
            return None
        banner = self._session.get(BannerData, favcategory)
        return banner.bannername if banner else None

    def add_registration(
        self,
        *,
        username: str,
        password_hash: str,
        account: Account,
        profile: Profile,
    ) -> None:
        self._session.add(account)
        self._session.add(profile)
        self._session.add(Signon(username=username, password=password_hash))
