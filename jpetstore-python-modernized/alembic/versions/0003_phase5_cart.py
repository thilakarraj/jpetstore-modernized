"""Revision 0003: persistent cart tables (Phase 5)."""

from alembic import op
import sqlalchemy as sa

revision = "0003_phase5_cart"
down_revision = "0002_phase2_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "cart",
        sa.Column("cart_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("userid", sa.String(length=80), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="active"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["userid"], ["account.userid"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("cart_id", name="pk_cart"),
        sa.UniqueConstraint("userid", name="uq_cart_userid"),
    )
    op.create_index("ix_cart_userid", "cart", ["userid"], unique=False)

    op.create_table(
        "cart_item",
        sa.Column("cart_item_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("cart_id", sa.Integer(), nullable=False),
        sa.Column("itemid", sa.String(length=10), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.CheckConstraint("quantity > 0", name="ck_cart_item_quantity_positive"),
        sa.ForeignKeyConstraint(["cart_id"], ["cart.cart_id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["itemid"], ["item.itemid"], name="fk_cart_item_item"),
        sa.PrimaryKeyConstraint("cart_item_id", name="pk_cart_item"),
        sa.UniqueConstraint("cart_id", "itemid", name="uq_cart_item_cart_itemid"),
    )
    op.create_index("ix_cart_item_cart_id", "cart_item", ["cart_id"], unique=False)
    op.create_index("ix_cart_item_itemid", "cart_item", ["itemid"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_cart_item_itemid", table_name="cart_item")
    op.drop_index("ix_cart_item_cart_id", table_name="cart_item")
    op.drop_table("cart_item")
    op.drop_index("ix_cart_userid", table_name="cart")
    op.drop_table("cart")
