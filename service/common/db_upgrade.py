import logging
from sqlalchemy import inspect, text

logger = logging.getLogger("flask.app")

EMAIL_PLACEHOLDER_SQL = "'customer-' || id || '@example.invalid'"


def upgrade_db(db):
    """Bring an existing database schema up to date with the models"""
    with db.engine.begin() as conn:
        if _is_up_to_date(conn):
            logger.info("Database schema is up to date; no upgrade needed")
            return
        _add_customer_email(conn)
    logger.info("Database schema upgrade complete")


def _is_up_to_date(conn):
    """Return True if the schema already has everything the upgrade adds"""
    columns = {col["name"]: col for col in inspect(conn).get_columns("customers")}
    email = columns.get("email")
    return (
        email is not None
        and not email["nullable"]
        and _constraint_exists(conn, "customers", "customers_email_key")
        and _constraint_exists(conn, "customers", "customers_email_not_blank")
    )


def _constraint_exists(conn, table, name):
    """Return True if the named constraint exists on the table"""
    return (
        conn.execute(
            text(
                "SELECT 1 FROM pg_constraint "
                "WHERE conrelid = CAST(:table AS regclass) AND conname = :name"
            ),
            {"table": table, "name": name},
        ).first()
        is not None
    )


def _add_customer_email(conn):
    """Add customers.email, backfill existing rows and apply its constraints"""
    logger.info("Upgrading database: adding customers.email")
    conn.execute(text("ALTER TABLE customers ADD COLUMN email VARCHAR(255)"))

    backfilled = conn.execute(
        text(f"UPDATE customers SET email = {EMAIL_PLACEHOLDER_SQL}")
    ).rowcount
    if backfilled:
        logger.warning(
            "Upgrading database: gave %d existing customers a placeholder "
            "email ending in @example.invalid",
            backfilled,
        )
    conn.execute(
        text(
            "ALTER TABLE customers "
            "ALTER COLUMN email SET NOT NULL, "
            "ADD CONSTRAINT customers_email_key UNIQUE (email), "
            r"ADD CONSTRAINT customers_email_not_blank CHECK (email ~ '\S')"
        )
    )
