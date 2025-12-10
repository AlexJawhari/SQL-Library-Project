import csv
from pathlib import Path
from db import get_db

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR.parent / "data"

def load_table_from_csv(conn, table, columns, csv_name):
    path = DATA_DIR / csv_name
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        rows = []
        for r in reader:
            rows.append(tuple(r[col] if r[col] != "" else None for col in columns))
    placeholders = ",".join(["?"] * len(columns))
    col_list = ",".join(columns)
    sql = f"INSERT INTO {table} ({col_list}) VALUES ({placeholders})"
    with conn:
        conn.executemany(sql, rows)
    print(f"Loaded {len(rows)} rows into {table} from {csv_name}")

def main():
    conn = get_db()

    load_table_from_csv(
        conn,
        "BOOK",
        ["isbn_primary", "isbn10", "isbn13", "title"],
        "book.csv",
    )

    load_table_from_csv(
        conn,
        "AUTHORS",
        ["author_id", "name"],
        "authors.csv",
    )

    load_table_from_csv(
        conn,
        "BOOK_AUTHORS",
        ["isbn_primary", "author_id"],
        "book_authors.csv",
    )

    load_table_from_csv(
        conn,
        "BORROWER",
        ["card_id", "ssn", "bname", "address", "phone"],
        "borrower.csv",
    )

    conn.close()

if __name__ == "__main__":
    main()
