from flask import Blueprint, jsonify, request
from db import get_db

bp = Blueprint("search", __name__, url_prefix="/api")


@bp.get("/search")
def search():
    # Get query parameter
    q = request.args.get("q", "").strip()
    
    if not q:
        return jsonify({"error": "No search query provided"}), 400

    conn = get_db()
    try:
        cursor = conn.cursor()

        # SQLite query
        sql = """
        SELECT
            b.isbn_primary AS isbn,
            b.title AS title,
            (
                SELECT GROUP_CONCAT(a.name, ', ')
                FROM AUTHORS a
                JOIN BOOK_AUTHORS ba ON ba.author_id = a.author_id
                WHERE ba.isbn_primary = b.isbn_primary
            ) AS authors,
            CASE
                WHEN EXISTS (
                    SELECT 1 FROM BOOK_LOANS bl
                    WHERE bl.isbn = b.isbn_primary AND bl.date_in IS NULL
                )
                THEN 1
                ELSE 0
            END AS checked_out,
            (
                SELECT bl.card_id
                FROM BOOK_LOANS bl
                WHERE bl.isbn = b.isbn_primary AND bl.date_in IS NULL
                LIMIT 1
            ) AS borrower_id
        FROM BOOK b
        WHERE
            LOWER(b.isbn_primary) LIKE LOWER(?) OR
            LOWER(b.isbn10) LIKE LOWER(?) OR
            LOWER(b.isbn13) LIKE LOWER(?) OR
            LOWER(b.title) LIKE LOWER(?) OR
            EXISTS (
                SELECT 1
                FROM AUTHORS a
                JOIN BOOK_AUTHORS ba ON ba.author_id = a.author_id
                WHERE ba.isbn_primary = b.isbn_primary AND LOWER(a.name) LIKE LOWER(?)
            )
        ORDER BY b.title
        """

        # Prepare search term
        like_q = f"%{q}%"
        cursor.execute(sql, (like_q, like_q, like_q, like_q, like_q))
        rows = cursor.fetchall()

        # Convert authors string to array
        results = []
        for row in rows:
            authors_list = row["authors"].split(", ") if row["authors"] else []
            results.append({
                "isbn": row["isbn"],
                "title": row["title"],
                "authors": authors_list,
                "checked_out": bool(row["checked_out"]),
                "borrower_id": row["borrower_id"]
            })

        return jsonify(results)
    except Exception as e:
        return jsonify({"error": "Database error", "details": str(e)}), 500
    finally:
        conn.close()