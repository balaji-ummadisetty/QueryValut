"""
database/connection.py
PostgreSQL connection management using psycopg2.
Returns RealDictCursor connections so rows are accessible by column name,
identical to how sqlite3.Row worked before.
"""
import psycopg2
import psycopg2.extras
from config.settings import settings


def get_conn() -> psycopg2.extensions.connection:
    """
    Open a PostgreSQL connection with RealDictCursor as default cursor factory.
    Rows returned from execute() are accessible by column name, e.g. row["id"].
    """
    conn = psycopg2.connect(
        settings.DATABASE_URL,
        cursor_factory=psycopg2.extras.RealDictCursor,
    )
    return conn
