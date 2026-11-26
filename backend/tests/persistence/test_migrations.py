from alembic import command
from alembic.migration import MigrationContext
from sqlalchemy import inspect, text

from app.models import Base


def test_downgrade_and_recreate_schema(pg_engine, migration_config):
    expected = {
        "requesters",
        "categories",
        "tickets",
        "ticket_history",
        "notifications",
    }
    assert set(Base.metadata.tables) == expected
    with pg_engine.begin() as connection:
        migration_config.attributes["connection"] = connection
        assert set(inspect(connection).get_table_names()) == expected | {
            "alembic_version"
        }
        command.downgrade(migration_config, "base")
    with pg_engine.begin() as connection:
        migration_config.attributes["connection"] = connection
        assert inspect(connection).get_table_names() == ["alembic_version"]
        assert not inspect(connection).get_enums()
        assert (
            connection.scalar(
                text("SELECT to_regprocedure('helpdesk_set_updated_at()')")
            )
            is None
        )
        command.upgrade(migration_config, "head")
    with pg_engine.begin() as connection:
        migration_config.attributes["connection"] = connection
        assert set(inspect(connection).get_table_names()) == expected | {
            "alembic_version"
        }
        assert (
            MigrationContext.configure(connection).get_current_revision()
            == "0002_delivery"
        )
        command.check(migration_config)


def test_upgrade_preserves_stage_three_deliveries(session, ticket, migration_config):
    connection = session.connection()
    migration_config.attributes["connection"] = connection
    command.downgrade(migration_config, "0001_helpdesk")
    connection.execute(
        text("""
            INSERT INTO notifications (ticket_id, channel, recipient, status,
                                       attempt_count, last_attempt_at, sent_at)
            VALUES (:id, 'EMAIL', 'ti', 'PENDING', 0, NULL, NULL),
                   (:id, 'TEAMS', 'ti', 'SENT', 2, now(), now())
        """),
        {"id": ticket.id},
    )
    command.upgrade(migration_config, "head")
    rows = connection.execute(
        text("""
            SELECT status, attempt_count, cycle_attempt, delivery_mode, claim_token
            FROM notifications WHERE ticket_id = :id ORDER BY id
        """),
        {"id": ticket.id},
    ).all()
    assert rows == [("PENDING", 0, 0, None, None), ("SENT", 2, 0, None, None)]
