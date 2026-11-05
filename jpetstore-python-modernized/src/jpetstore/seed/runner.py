"""Idempotent database seeding for development and test environments."""

from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from jpetstore.config import Settings
from jpetstore.logging_setup import get_logger
from jpetstore.models import (
    Account,
    BannerData,
    Category,
    Inventory,
    Item,
    Product,
    Profile,
    Sequence,
    Signon,
    Supplier,
)
from jpetstore.security.passwords import hash_password
from jpetstore.seed.legacy_data import (
    ACCOUNTS,
    BANNERS,
    CATEGORIES,
    DEMO_ACCOUNT_PASSWORDS,
    INVENTORY_QTY,
    ITEMS,
    ITEM_IDS,
    PRODUCTS,
    PROFILES,
    SEQUENCE_ORDERNUM,
    SUPPLIERS,
)

logger = get_logger("seed")


def _upsert(session: Session, entity: object) -> None:
    session.merge(entity)


def seed_development_data(session: Session, settings: Settings) -> None:
    """Load legacy demo data; safe to call multiple times."""
    if settings.app_env == "production":
        raise RuntimeError("Refusing to seed data in production environment")

    seq_name, seq_next = SEQUENCE_ORDERNUM
    _upsert(session, Sequence(name=seq_name, nextid=seq_next))

    for row in SUPPLIERS:
        _upsert(
            session,
            Supplier(
                suppid=row[0],
                name=row[1],
                status=row[2],
                addr1=row[3],
                addr2=row[4],
                city=row[5],
                state=row[6],
                zip=row[7],
                phone=row[8],
            ),
        )

    for favcategory, bannername in BANNERS:
        _upsert(session, BannerData(favcategory=favcategory, bannername=bannername))

    for catid, name, descn in CATEGORIES:
        _upsert(session, Category(catid=catid, name=name, descn=descn))

    for productid, category, name, descn in PRODUCTS:
        _upsert(
            session,
            Product(productid=productid, category=category, name=name, descn=descn),
        )

    for account in ACCOUNTS:
        _upsert(session, Account(**account))

    for profile in PROFILES:
        _upsert(session, Profile(**profile))

    for username, plain in DEMO_ACCOUNT_PASSWORDS.items():
        existing = session.get(Signon, username)
        password_hash = hash_password(plain)
        if existing is None:
            session.add(Signon(username=username, password=password_hash))
        else:
            existing.password = password_hash

    for item_row in ITEMS:
        itemid, productid, listprice, unitcost, supplier, status, attr1 = item_row
        _upsert(
            session,
            Item(
                itemid=itemid,
                productid=productid,
                listprice=listprice,
                unitcost=unitcost,
                supplier=supplier,
                status=status,
                attr1=attr1,
            ),
        )

    for item_id in ITEM_IDS:
        _upsert(session, Inventory(itemid=item_id, qty=INVENTORY_QTY))

    session.commit()
    logger.info(
        "Development seed completed",
        extra={"event": "seed.completed", "categories": len(CATEGORIES), "items": len(ITEMS)},
    )


def count_categories(session: Session) -> int:
    return session.scalar(select(func.count()).select_from(Category)) or 0
