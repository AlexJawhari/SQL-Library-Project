from flask import Blueprint, jsonify, request
from db import get_db

bp = Blueprint("loans", __name__, url_prefix="/api")


@bp.post("/checkout")
def checkout():
    # TODO: enforce rules (3-loan limit, already out, fines block).
    # Body: { isbn, borrower_card_no }
    # SQLite uses ? placeholders (not %s)
    # date_out = today, due_date = today + 14 days
    # Use date.today().isoformat() for date strings

    #First, check user input.
    parameters = request.get_json(silent=True)

    isbn = (parameters.get("isbn") or "").strip()
    card_id = (parameters.get("card_id") or "").strip()

    if not isbn or not card_id:
        return jsonify({"error": "Missing ISBN or Card #"}), 400

    #Next, begin connecting to the database.
    db = get_db()

    try:
        cur = db.cursor()

        #The following section is dedicated to enforcing the rules surrounding library users and book checkouts.
        cur.execute("SELECT COUNT(*) FROM BOOK_LOANS WHERE card_id = ? AND date_in IS NULL", (card_id,))
        num_borrowed = cur.fetchone()
        if num_borrowed >= 3:
            return jsonify({"error": "Too many books on loan already", "num_borrowed": num_borrowed}), 412

        cur.execute("SELECT isbn FROM BOOK_LOANS WHERE isbn = ? AND date_in IS NULL", (isbn,))
        book_already_borrowed = cur.fetchone()
        if book_already_borrowed:
            return jsonify({"error": "Book is already on loan", "book_already_borrowed": book_already_borrowed}), 409

        cur.execute(
            """
            SELECT COUNT(*) 
            FROM FINES as f 
            JOIN BOOK_LOANS as bl on bl.loan_id = f.loan_id 
            JOIN BORROWER as b on b.card_id = ? 
            WHERE f.paid = 0
            """,
            (card_id,)
        )
        num_fines = cur.fetchone()
        if num_fines > 0:
            return jsonify({"error": "Fines must be paid first", "num_fines": num_fines}), 403

        #Now, we can safely perform the work.
        cur.execute("INSERT INTO BOOK_LOANS (isbn, card_id, date_out, due_date) VALUES (?, ?, ?, ?)",
                    (isbn, card_id, date.today().isoformat(), (date.today() + timedelta(days=14)).isoformat(),))
        db.commit()

        return jsonify({"isbn": isbn, "card_id": card_id}), 201
    except Exception as e:
        db.rollback()
        return jsonify({"error": "Database error", "details": str(e)}), 500
    finally:
        db.close()


@bp.post("/checkout/batch")
def checkout_batch():
    # TODO: loop over isbns, reuse checkout logic.
    # Body: { isbns: [], borrower_card_no: "" }
    return jsonify({"error": "not implemented"}), 501


@bp.post("/checkin")
def checkin():
    # TODO: set date_in = today for given loan_id.
    # Body: { loan_id: number }
    # SQLite uses ? placeholders (not %s)
    return jsonify({"error": "not implemented"}), 501

