"""Revision 0002: full JPetStore schema (Phase 2)."""

from alembic import op
import sqlalchemy as sa

revision = "0002_phase2_schema"
down_revision = "0001_phase1_baseline"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "supplier",
        sa.Column("suppid", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=80), nullable=True),
        sa.Column("status", sa.String(length=2), nullable=False),
        sa.Column("addr1", sa.String(length=80), nullable=True),
        sa.Column("addr2", sa.String(length=80), nullable=True),
        sa.Column("city", sa.String(length=80), nullable=True),
        sa.Column("state", sa.String(length=80), nullable=True),
        sa.Column("zip", sa.String(length=5), nullable=True),
        sa.Column("phone", sa.String(length=80), nullable=True),
        sa.PrimaryKeyConstraint("suppid", name="pk_supplier"),
    )
    op.create_table(
        "category",
        sa.Column("catid", sa.String(length=10), nullable=False),
        sa.Column("name", sa.String(length=80), nullable=True),
        sa.Column("descn", sa.String(length=255), nullable=True),
        sa.PrimaryKeyConstraint("catid", name="pk_category"),
    )
    op.create_table(
        "bannerdata",
        sa.Column("favcategory", sa.String(length=80), nullable=False),
        sa.Column("bannername", sa.String(length=255), nullable=True),
        sa.PrimaryKeyConstraint("favcategory", name="pk_bannerdata"),
    )
    op.create_table(
        "account",
        sa.Column("userid", sa.String(length=80), nullable=False),
        sa.Column("email", sa.String(length=80), nullable=False),
        sa.Column("firstname", sa.String(length=80), nullable=False),
        sa.Column("lastname", sa.String(length=80), nullable=False),
        sa.Column("status", sa.String(length=2), nullable=True),
        sa.Column("addr1", sa.String(length=80), nullable=False),
        sa.Column("addr2", sa.String(length=40), nullable=True),
        sa.Column("city", sa.String(length=80), nullable=False),
        sa.Column("state", sa.String(length=80), nullable=False),
        sa.Column("zip", sa.String(length=20), nullable=False),
        sa.Column("country", sa.String(length=20), nullable=False),
        sa.Column("phone", sa.String(length=80), nullable=False),
        sa.PrimaryKeyConstraint("userid", name="pk_account"),
    )
    op.create_table(
        "signon",
        sa.Column("username", sa.String(length=25), nullable=False),
        sa.Column("password", sa.String(length=255), nullable=False),
        sa.PrimaryKeyConstraint("username", name="pk_signon"),
    )
    op.create_table(
        "profile",
        sa.Column("userid", sa.String(length=80), nullable=False),
        sa.Column("langpref", sa.String(length=80), nullable=False),
        sa.Column("favcategory", sa.String(length=30), nullable=True),
        sa.Column("mylistopt", sa.Integer(), nullable=True),
        sa.Column("banneropt", sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint("userid", name="pk_profile"),
    )
    op.create_table(
        "product",
        sa.Column("productid", sa.String(length=10), nullable=False),
        sa.Column("category", sa.String(length=10), nullable=False),
        sa.Column("name", sa.String(length=80), nullable=True),
        sa.Column("descn", sa.String(length=255), nullable=True),
        sa.ForeignKeyConstraint(["category"], ["category.catid"], name="fk_product_1"),
        sa.PrimaryKeyConstraint("productid", name="pk_product"),
    )
    op.create_index("productCat", "product", ["category"], unique=False)
    op.create_index("productName", "product", ["name"], unique=False)
    op.create_table(
        "item",
        sa.Column("itemid", sa.String(length=10), nullable=False),
        sa.Column("productid", sa.String(length=10), nullable=False),
        sa.Column("listprice", sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column("unitcost", sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column("supplier", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(length=2), nullable=True),
        sa.Column("attr1", sa.String(length=80), nullable=True),
        sa.Column("attr2", sa.String(length=80), nullable=True),
        sa.Column("attr3", sa.String(length=80), nullable=True),
        sa.Column("attr4", sa.String(length=80), nullable=True),
        sa.Column("attr5", sa.String(length=80), nullable=True),
        sa.ForeignKeyConstraint(["productid"], ["product.productid"], name="fk_item_1"),
        sa.ForeignKeyConstraint(["supplier"], ["supplier.suppid"], name="fk_item_2"),
        sa.PrimaryKeyConstraint("itemid", name="pk_item"),
    )
    op.create_index("itemProd", "item", ["productid"], unique=False)
    op.create_table(
        "inventory",
        sa.Column("itemid", sa.String(length=10), nullable=False),
        sa.Column("qty", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("itemid", name="pk_inventory"),
    )
    op.create_table(
        "orders",
        sa.Column("orderid", sa.Integer(), nullable=False),
        sa.Column("userid", sa.String(length=80), nullable=False),
        sa.Column("orderdate", sa.Date(), nullable=False),
        sa.Column("shipaddr1", sa.String(length=80), nullable=False),
        sa.Column("shipaddr2", sa.String(length=80), nullable=True),
        sa.Column("shipcity", sa.String(length=80), nullable=False),
        sa.Column("shipstate", sa.String(length=80), nullable=False),
        sa.Column("shipzip", sa.String(length=20), nullable=False),
        sa.Column("shipcountry", sa.String(length=20), nullable=False),
        sa.Column("billaddr1", sa.String(length=80), nullable=False),
        sa.Column("billaddr2", sa.String(length=80), nullable=True),
        sa.Column("billcity", sa.String(length=80), nullable=False),
        sa.Column("billstate", sa.String(length=80), nullable=False),
        sa.Column("billzip", sa.String(length=20), nullable=False),
        sa.Column("billcountry", sa.String(length=20), nullable=False),
        sa.Column("courier", sa.String(length=80), nullable=False),
        sa.Column("totalprice", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("billtofirstname", sa.String(length=80), nullable=False),
        sa.Column("billtolastname", sa.String(length=80), nullable=False),
        sa.Column("shiptofirstname", sa.String(length=80), nullable=False),
        sa.Column("shiptolastname", sa.String(length=80), nullable=False),
        sa.Column("creditcard", sa.String(length=80), nullable=False),
        sa.Column("exprdate", sa.String(length=7), nullable=False),
        sa.Column("cardtype", sa.String(length=80), nullable=False),
        sa.Column("locale", sa.String(length=80), nullable=False),
        sa.PrimaryKeyConstraint("orderid", name="pk_orders"),
    )
    op.create_table(
        "orderstatus",
        sa.Column("orderid", sa.Integer(), nullable=False),
        sa.Column("linenum", sa.Integer(), nullable=False),
        sa.Column("timestamp", sa.Date(), nullable=False),
        sa.Column("status", sa.String(length=2), nullable=False),
        sa.PrimaryKeyConstraint("orderid", "linenum", name="pk_orderstatus"),
    )
    op.create_table(
        "lineitem",
        sa.Column("orderid", sa.Integer(), nullable=False),
        sa.Column("linenum", sa.Integer(), nullable=False),
        sa.Column("itemid", sa.String(length=10), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("unitprice", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.PrimaryKeyConstraint("orderid", "linenum", name="pk_lineitem"),
    )
    op.create_table(
        "sequence",
        sa.Column("name", sa.String(length=30), nullable=False),
        sa.Column("nextid", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("name", name="pk_sequence"),
    )


def downgrade() -> None:
    op.drop_table("sequence")
    op.drop_table("lineitem")
    op.drop_table("orderstatus")
    op.drop_table("orders")
    op.drop_table("inventory")
    op.drop_index("itemProd", table_name="item")
    op.drop_table("item")
    op.drop_index("productName", table_name="product")
    op.drop_index("productCat", table_name="product")
    op.drop_table("product")
    op.drop_table("profile")
    op.drop_table("signon")
    op.drop_table("account")
    op.drop_table("bannerdata")
    op.drop_table("category")
    op.drop_table("supplier")
