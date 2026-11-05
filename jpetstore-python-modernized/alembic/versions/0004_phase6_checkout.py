"""Revision 0004: checkout idempotency and inventory non-negative guard."""

from alembic import op
import sqlalchemy as sa

revision = "0004_phase6_checkout"
down_revision = "0003_phase5_cart"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "checkout_idempotency",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("userid", sa.String(length=80), nullable=False),
        sa.Column("idempotency_key", sa.String(length=128), nullable=False),
        sa.Column("request_fingerprint", sa.String(length=64), nullable=False),
        sa.Column("orderid", sa.Integer(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["userid"], ["account.userid"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["orderid"], ["orders.orderid"], name="fk_checkout_idem_order"),
        sa.PrimaryKeyConstraint("id", name="pk_checkout_idempotency"),
        sa.UniqueConstraint("userid", "idempotency_key", name="uq_checkout_idem_user_key"),
    )
    bind = op.get_bind()
    if bind.dialect.name == "mysql":
        op.create_check_constraint(
            "ck_inventory_qty_non_negative",
            "inventory",
            "qty >= 0",
        )


def downgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "mysql":
        op.drop_constraint("ck_inventory_qty_non_negative", "inventory", type_="check")
    op.drop_table("checkout_idempotency")
