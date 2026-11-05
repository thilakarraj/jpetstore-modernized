"""ORM model constraint and relationship tests."""

from decimal import Decimal

import pytest
from sqlalchemy.exc import IntegrityError

from jpetstore.models import Account, Category, Item, Product, Sequence, Signon, Supplier


def test_category_product_relationship(db_session) -> None:
    db_session.add(Category(catid="FISH", name="Fish", descn="desc"))
    db_session.add(
        Product(productid="FI-SW-01", category="FISH", name="Angelfish", descn="d")
    )
    db_session.flush()
    product = db_session.get(Product, "FI-SW-01")
    assert product is not None
    assert product.category == "FISH"


def test_item_requires_valid_product_fk(db_session) -> None:
    db_session.add(Category(catid="FISH", name="Fish", descn=None))
    db_session.add(Product(productid="FI-SW-01", category="FISH", name="A", descn=None))
    db_session.flush()
    db_session.add(
        Item(
            itemid="EST-1",
            productid="FI-SW-01",
            listprice=Decimal("1.00"),
            unitcost=Decimal("1.00"),
            supplier=None,
            status="P",
            attr1=None,
        )
    )
    db_session.flush()
    with pytest.raises(IntegrityError):
        db_session.add(
            Item(
                itemid="EST-99",
                productid="MISSING",
                listprice=Decimal("1.00"),
                unitcost=None,
                supplier=None,
                status="P",
                attr1=None,
            )
        )
        db_session.flush()


def test_signon_primary_key_unique(db_session) -> None:
    db_session.add(Signon(username="j2ee", password="hash1"))
    db_session.flush()
    db_session.add(Signon(username="j2ee", password="hash2"))
    with pytest.raises(IntegrityError):
        db_session.flush()


def test_account_required_fields(db_session) -> None:
    account = Account(
        userid="u1",
        email="a@example.com",
        firstname="A",
        lastname="B",
        status="OK",
        addr1="1 Main",
        addr2=None,
        city="City",
        state="ST",
        zip="00000",
        country="USA",
        phone="555",
    )
    db_session.add(account)
    db_session.flush()
    assert db_session.get(Account, "u1") is not None


def test_sequence_row(db_session) -> None:
    db_session.add(Sequence(name="ordernum", nextid=1000))
    db_session.flush()
    row = db_session.get(Sequence, "ordernum")
    assert row is not None
    assert row.nextid == 1000


def test_supplier_optional_on_item(db_session) -> None:
    db_session.add(Category(catid="FISH", name="Fish", descn=None))
    db_session.add(Product(productid="P1", category="FISH", name="N", descn=None))
    db_session.add(Supplier(suppid=1, name="S", status="AC", addr1=None, addr2=None, city=None, state=None, zip=None, phone=None))
    db_session.flush()
    db_session.add(
        Item(
            itemid="I1",
            productid="P1",
            listprice=Decimal("1"),
            unitcost=Decimal("1"),
            supplier=1,
            status="P",
            attr1=None,
        )
    )
    db_session.flush()
