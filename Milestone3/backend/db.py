import sqlite3
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DB_PATH = Path(__file__).resolve().parent / "library.db"


def get_db():
    """Return a new SQLite connection with row factory for dict-like access."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn

