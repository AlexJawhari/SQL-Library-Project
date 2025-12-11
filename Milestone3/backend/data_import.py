import csv
from pathlib import Path
from db import get_db

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR.parent / "data"

def load_table_from_csv(conn, table, columns, csv_name, clear_first=False):
    path = DATA_DIR / csv_name
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        rows = []
        seen = set()
        for r in reader:
            row_tuple = tuple(r[col] if r[col] != "" else None for col in columns)
            if row_tuple not in seen:
                rows.append(row_tuple)
                seen.add(row_tuple)
    placeholders = ",".join(["?"] * len(columns))
    col_list = ",".join(columns)
    
    with conn:
        if clear_first:
            conn.execute(f"DELETE FROM {table}")
        sql = f"INSERT OR IGNORE INTO {table} ({col_list}) VALUES ({placeholders})"
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
