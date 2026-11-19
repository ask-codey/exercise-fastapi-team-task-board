"""Crew Board's database: where the file is, how a connection is opened, the migrations, and get_db, the dependency
that gives every request its own connection. Ready to use: you don't need to change this file."""
import sqlite3
from pathlib import Path

# The database file, beside this file. The tests never touch it: they use a throwaway file of their own.
DATABASE_PATH = Path(__file__).parent / "crew_board.db"

# The numbered migration scripts: 0001_create_users.sql, 0002_create_tasks.sql, ...
MIGRATIONS = Path(__file__).parent / "migrations"


def open_db(path):
    """Opens the database file at path.

    - row_factory = sqlite3.Row: rows can be read by column name, and dict(row) turns one into a dictionary.
    - PRAGMA foreign_keys = ON: SQLite checks REFERENCES only when this is on.
    - check_same_thread=False: FastAPI may open a request's connection in one of its threads and use it in another,
      so the connection mustn't refuse that. It's safe because each request gets a connection of its own.
    """
    conn = sqlite3.connect(path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def migrate(conn):
    """Runs, in order, every script in migrations/ whose number is higher than the database's PRAGMA user_version,
    and sets user_version to each script's number after it runs. Returns the numbers it ran, such as [1, 2, 3], or []
    when the database is up to date."""
    version = conn.execute("PRAGMA user_version").fetchone()[0]
    ran = []
    for path in sorted(MIGRATIONS.glob("*.sql")):
        number = int(path.name[:4])
        if number > version:
            conn.executescript(path.read_text(encoding="utf-8"))
            # PRAGMA takes no placeholders. number is an int from our own file name, never from a request.
            conn.execute(f"PRAGMA user_version = {number}")
            conn.commit()
            ran.append(number)
    return ran


def get_db():
    """Gives each request its own connection to DATABASE_PATH: hands it to the route with yield, commits when the
    request finishes without an error, rolls back when it raises one (and raises it again), and always closes it.
    FastAPI runs it once per request, even when a route and get_current_user both depend on it, so they share one
    connection."""
    conn = open_db(DATABASE_PATH)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
