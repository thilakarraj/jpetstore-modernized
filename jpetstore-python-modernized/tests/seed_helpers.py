"""Shared test database seed helpers."""

from sqlalchemy.orm import Session

from jpetstore.models import BannerData, Category, Inventory, Item, Product, Supplier
from jpetstore.models import Sequence
from jpetstore.seed import legacy_data


def seed_catalog(session: Session) -> None:
    for catid, name, descn in legacy_data.CATEGORIES:
        session.add(Category(catid=catid, name=name, descn=descn))
    for suppid, name, status, a1, a2, city, state, zip_, phone in legacy_data.SUPPLIERS:
        session.add(
            Supplier(
                suppid=suppid,
                name=name,
                status=status,
                addr1=a1,
                addr2=a2 or None,
                city=city,
                state=state,
                zip=zip_,
                phone=phone,
            )
        )
    for fav, html in legacy_data.BANNERS:
        session.add(BannerData(favcategory=fav, bannername=html))
    for productid, category, name, descn in legacy_data.PRODUCTS:
        session.add(
            Product(productid=productid, category=category, name=name, descn=descn)
        )
    for row in legacy_data.ITEMS:
        itemid, productid, listprice, unitcost, supplier, status, attr1 = row
        session.add(
            Item(
                itemid=itemid,
                productid=productid,
                listprice=listprice,
                unitcost=unitcost,
                supplier=supplier,
                status=status,
                attr1=attr1,
                attr2=None,
                attr3=None,
                attr4=None,
                attr5=None,
            )
        )
    for itemid in legacy_data.ITEM_IDS:
        session.add(Inventory(itemid=itemid, qty=legacy_data.INVENTORY_QTY))
    name, nextid = legacy_data.SEQUENCE_ORDERNUM
    session.add(Sequence(name=name, nextid=nextid))
    session.commit()


def ensure_catalog_seeded(session: Session) -> None:
    """Seed catalog data once; safe when jpetstore_test already has development seed rows."""
    if session.get(Sequence, "ordernum") is not None:
        return
    seed_catalog(session)
