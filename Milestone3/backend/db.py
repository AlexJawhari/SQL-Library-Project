import pymysql
from pathlib import Path

# MySQL connection settings (fill in your local values)
MYSQL_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "library_demo",
    "cursorclass": pymysql.cursors.DictCursor,
    "charset": "utf8mb4",
    "autocommit": True,
}

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def get_db():
    """Return a new MySQL connection. Swap for pooling if desired."""
    return pymysql.connect(**MYSQL_CONFIG)

