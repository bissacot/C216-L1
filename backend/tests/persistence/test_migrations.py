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
            == "0001_helpdesk"
        )
        command.check(migration_config)
