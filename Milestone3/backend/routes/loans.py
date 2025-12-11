from datetime import date, timedelta
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

        cur.execute("SELECT * FROM BOOK_LOANS WHERE isbn = ?", (isbn,))
        result = cur.fetchone()
        return jsonify({"loan_id": result["loan_id"], "isbn": isbn, "card_id": card_id, "date_out": result["date_out"], "due_date": result["due_date"]}), 201
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

    parameters = request.get_json(silent=True)

    isbn = (parameters.get("isbn") or "").strip()
    card_id = (parameters.get("card_id") or "").strip()
    bname = (parameters.get("bname") or "").strip()

    db = get_db()

    try:
        cur = db.cursor()

        # Placeholder for returning later.
        placeholder_isbn = ""

        # Search is performed preferentially: ISBN > CARD_ID > BNAME
        if isbn:
            placeholder_isbn = isbn
            cur.execute("UPDATE BOOK_LOANS SET date_in = ? WHERE isbn = ? AND date_in IS NULL", (date.today().isoformat(), isbn,))
        elif card_id:
            # Selects the first book (yet to be checked in) that matches the user's card; ambiguity is introduced here without an isbn.
            cur.execute("SELECT isbn FROM BOOK_LOANS WHERE card_id = ? AND date_in IS NULL", (card_id,))
            temp_book = cur.fetchone()
            placeholder_isbn = temp_book
            cur.execute("UPDATE BOOK_LOANS SET date_in = ? WHERE isbn = ? AND date_in IS NULL", (date.today().isoformat(), temp_book,))
        elif bname:
            # Even more ambiguous than card_id, since the name substr could refer to multiple borrowers.
            cur.execute("SELECT card_id FROM BORROWER WHERE bname LIKE CONCAT('%', ?, '%')", (bname,))
            temp_card_id = cur.fetchone()
            cur.execute("SELECT isbn FROM BOOK_LOANS WHERE card_id = ? AND date_in IS NULL", (temp_card_id,))
            temp_book = cur.fetchone()
            placeholder_isbn = temp_book
            cur.execute("UPDATE BOOK_LOANS SET date_in = ? WHERE isbn = ? AND date_in IS NULL", (date.today().isoformat(), temp_book,))
        else:
            # No search parameters were provided.
            return jsonify({"error": "Missing search fields"}), 400

        db.commit()

        cur.execute("SELECT loan_id FROM BOOK_LOANS WHERE isbn = ?", (placeholder_isbn,))
        result = cur.fetchone()
        return jsonify({"loan_id": result, "date_in": date.today().isoformat()}), 200
    except Exception as e:
        db.rollback()
        return jsonify({"error": "Database error", "details": str(e)}), 500
    finally:
        db.close()
