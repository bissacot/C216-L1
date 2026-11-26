"""Reservas recuperáveis e política de tentativas da outbox."""

import sqlalchemy as sa
from alembic import op

revision = "0002_delivery"
down_revision = "0001_helpdesk"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("notifications", sa.Column("delivery_mode", sa.String(4)))
    op.add_column("notifications", sa.Column("claim_token", sa.String(32)))
    op.add_column("notifications", sa.Column("lease_until", sa.DateTime(timezone=True)))
    op.add_column(
        "notifications", sa.Column("next_attempt_at", sa.DateTime(timezone=True))
    )
    op.add_column(
        "notifications",
        sa.Column("cycle_attempt", sa.Integer(), nullable=False, server_default="0"),
    )
    op.create_check_constraint(
        "ck_delivery_mode", "notifications", "delivery_mode IN ('LIVE', 'MOCK')"
    )
    op.create_check_constraint(
        "ck_delivery_cycle",
        "notifications",
        "cycle_attempt BETWEEN 0 AND attempt_count",
    )
    op.create_check_constraint(
        "ck_delivery_lease",
        "notifications",
        "(claim_token IS NULL) = (lease_until IS NULL) "
        "AND (claim_token IS NULL OR status = 'PENDING')",
    )
    op.create_index(
        "ix_delivery_due",
        "notifications",
        ["channel", "status", "next_attempt_at", "id"],
    )


def downgrade() -> None:
    op.drop_index("ix_delivery_due", table_name="notifications")
    for name in ("ck_delivery_lease", "ck_delivery_cycle", "ck_delivery_mode"):
        op.drop_constraint(name, "notifications", type_="check")
    for name in (
        "cycle_attempt",
        "next_attempt_at",
        "lease_until",
        "claim_token",
        "delivery_mode",
    ):
        op.drop_column("notifications", name)
