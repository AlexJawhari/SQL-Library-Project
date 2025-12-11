from flask import Blueprint, jsonify, request
from db import get_db

bp = Blueprint("search", __name__, url_prefix="/api")


@bp.get("/search")
def search():
    # Get query parameter
    q = request.args.get("q", "").strip()
    
    if not q:
        return jsonify({"error": "No search query provided"}), 400

    db = get_db()
    cursor = db.cursor()

    # SQLite query
    sql = """
    SELECT
        b.isbn AS isbn,
        b.title AS title,
        (
            SELECT GROUP_CONCAT(a.name, ', ')
            FROM authors a
            JOIN book_authors ba ON ba.author_id = a.author_id
            WHERE ba.isbn = b.isbn
        ) AS authors,
        CASE
            WHEN EXISTS (
                SELECT 1 FROM book_loans bl
                WHERE bl.isbn = b.isbn AND bl.date_in IS NULL
            )
            THEN 1
            ELSE 0
        END AS checked_out,
        (
            SELECT bl.card_id
            FROM book_loans bl
            WHERE bl.isbn = b.isbn AND bl.date_in IS NULL
            LIMIT 1
        ) AS borrower_id
    FROM book b
    WHERE
        LOWER(b.isbn) LIKE LOWER(?) OR
        LOWER(b.title) LIKE LOWER(?) OR
        EXISTS (
            SELECT 1
            FROM authors a
            JOIN book_authors ba ON ba.author_id = a.author_id
            WHERE ba.isbn = b.isbn AND LOWER(a.name) LIKE LOWER(?)
        )
    ORDER BY b.title
    """

    # Prepare search term
    like_q = f"%{q}%"
    cursor.execute(sql, (like_q, like_q, like_q))
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