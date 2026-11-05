"""Account domain ORM models."""

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from jpetstore.models.base import Base


class Account(Base):
    __tablename__ = "account"

    userid: Mapped[str] = mapped_column(String(80), primary_key=True)
    email: Mapped[str] = mapped_column(String(80), nullable=False)
    firstname: Mapped[str] = mapped_column(String(80), nullable=False)
    lastname: Mapped[str] = mapped_column(String(80), nullable=False)
    status: Mapped[str | None] = mapped_column(String(2))
    addr1: Mapped[str] = mapped_column(String(80), nullable=False)
    addr2: Mapped[str | None] = mapped_column(String(40))
    city: Mapped[str] = mapped_column(String(80), nullable=False)
    state: Mapped[str] = mapped_column(String(80), nullable=False)
    zip: Mapped[str] = mapped_column(String(20), nullable=False)
    country: Mapped[str] = mapped_column(String(20), nullable=False)
    phone: Mapped[str] = mapped_column(String(80), nullable=False)


class Profile(Base):
    """Legacy schema: no FK constraint to account; logical 1:1 on userid."""

    __tablename__ = "profile"

    userid: Mapped[str] = mapped_column(String(80), primary_key=True)
    langpref: Mapped[str] = mapped_column(String(80), nullable=False)
    favcategory: Mapped[str | None] = mapped_column(String(30))
    mylistopt: Mapped[int | None] = mapped_column(Integer)
    banneropt: Mapped[int | None] = mapped_column(Integer)


class Signon(Base):
    __tablename__ = "signon"

    username: Mapped[str] = mapped_column(String(25), primary_key=True)
    # Wider than legacy (25) to store bcrypt hashes — see project docs/ADR.md SEC-P2-001.
    password: Mapped[str] = mapped_column(String(255), nullable=False)
