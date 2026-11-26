"""Estrutura inicial de chamados, histórico e notificações."""

import sqlalchemy as sa
from alembic import op

revision = "0001_helpdesk"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "categories",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint("btrim(name) <> ''", name="ck_categories_name"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_table(
        "requesters",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("email", sa.String(length=254), nullable=False),
        sa.Column("department", sa.String(length=150), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint("btrim(email) <> ''", name="ck_requesters_email"),
        sa.CheckConstraint("btrim(name) <> ''", name="ck_requesters_name"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "uq_requesters_email",
        "requesters",
        [sa.literal_column("lower(btrim(email))")],
        unique=True,
    )
    op.create_table(
        "tickets",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("requester_id", sa.Integer(), nullable=False),
        sa.Column("category_id", sa.Integer(), nullable=False),
        sa.Column(
            "priority",
            sa.Enum("LOW", "MEDIUM", "HIGH", "CRITICAL", name="ticket_priority"),
            server_default="MEDIUM",
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.Enum(
                "OPEN", "IN_PROGRESS", "RESOLVED", "CANCELLED", name="ticket_status"
            ),
            server_default="OPEN",
            nullable=False,
        ),
        sa.Column("assignee", sa.String(length=150), nullable=True),
        sa.Column("resolution", sa.Text(), nullable=True),
        sa.Column(
            "opened_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint("btrim(description) <> ''", name="ck_tickets_description"),
        sa.CheckConstraint("btrim(title) <> ''", name="ck_tickets_title"),
        sa.ForeignKeyConstraint(
            ["category_id"], ["categories.id"], ondelete="RESTRICT"
        ),
        sa.ForeignKeyConstraint(
            ["requester_id"], ["requesters.id"], ondelete="RESTRICT"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_tickets_category_id"), "tickets", ["category_id"], unique=False
    )
    op.create_index(
        op.f("ix_tickets_requester_id"), "tickets", ["requester_id"], unique=False
    )
    op.create_table(
        "notifications",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("ticket_id", sa.Integer(), nullable=False),
        sa.Column(
            "channel",
            sa.Enum("EMAIL", "TEAMS", name="notification_channel"),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.Enum("PENDING", "SENT", "FAILED", name="notification_status"),
            server_default="PENDING",
            nullable=False,
        ),
        sa.Column("recipient", sa.String(length=120), nullable=False),
        sa.Column("attempt_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("last_error", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("last_attempt_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(
            "(status = 'SENT') = (sent_at IS NOT NULL)", name="ck_notifications_sent"
        ),
        sa.CheckConstraint(
            "recipient ~ '^[a-z][a-z0-9._-]*$'", name="ck_notifications_alias"
        ),
        sa.CheckConstraint(
            "status = 'PENDING' OR attempt_count > 0",
            name="ck_notifications_attempted_status",
        ),
        sa.CheckConstraint(
            "(attempt_count = 0 AND last_attempt_at IS NULL) OR "
            "(attempt_count > 0 AND last_attempt_at IS NOT NULL)",
            name="ck_notifications_attempt",
        ),
        sa.ForeignKeyConstraint(["ticket_id"], ["tickets.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "ticket_id", "channel", "recipient", name="uq_notifications_destination"
        ),
    )
    op.create_index(
        "ix_notifications_status_last_attempt",
        "notifications",
        ["status", "last_attempt_at"],
        unique=False,
    )
    op.create_table(
        "ticket_history",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("ticket_id", sa.Integer(), nullable=False),
        sa.Column("field_name", sa.String(length=100), nullable=False),
        sa.Column("old_value", sa.Text(), nullable=True),
        sa.Column("new_value", sa.Text(), nullable=True),
        sa.Column("changed_by", sa.String(length=150), nullable=True),
        sa.Column(
            "changed_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint("btrim(field_name) <> ''", name="ck_history_field_name"),
        sa.ForeignKeyConstraint(["ticket_id"], ["tickets.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_history_ticket_changed",
        "ticket_history",
        ["ticket_id", "changed_at"],
        unique=False,
    )

    op.execute("""
        CREATE FUNCTION helpdesk_set_updated_at() RETURNS trigger
        LANGUAGE plpgsql AS $$
        BEGIN
            NEW.updated_at := statement_timestamp();
            RETURN NEW;
        END;
        $$
    """)
    for table in ("requesters", "categories", "tickets"):
        op.execute(
            f"CREATE TRIGGER set_updated_at BEFORE UPDATE ON {table} "
            "FOR EACH ROW EXECUTE FUNCTION helpdesk_set_updated_at()"
        )


def downgrade() -> None:
    for table in (
        "notifications",
        "ticket_history",
        "tickets",
        "requesters",
        "categories",
    ):
        op.drop_table(table)
    op.execute("DROP FUNCTION helpdesk_set_updated_at()")
    for name in (
        "notification_channel",
        "notification_status",
        "ticket_priority",
        "ticket_status",
    ):
        sa.Enum(name=name).drop(op.get_bind(), checkfirst=False)
