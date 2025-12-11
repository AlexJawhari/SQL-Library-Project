from datetime import date, timedelta
from flask import Blueprint, jsonify, request
from db import get_db

bp = Blueprint("loans", __name__, url_prefix="/api")


def has_unpaid_fines(cursor, card_id):
    """Check if borrower has any unpaid fines."""
    cursor.execute("""
        SELECT COUNT(*) as count
        FROM FINES f
        JOIN BOOK_LOANS bl ON f.loan_id = bl.loan_id
        WHERE bl.card_id = ? AND f.paid = 0
    """, (card_id,))
    result = cursor.fetchone()
    return result["count"] > 0 if result else False


def get_active_loan_count(cursor, card_id):
    """Get count of active loans for a borrower."""
    cursor.execute("""
        SELECT COUNT(*) as count
        FROM BOOK_LOANS
        WHERE card_id = ? AND date_in IS NULL
    """, (card_id,))
    result = cursor.fetchone()
    return result["count"] if result else 0


def is_book_checked_out(cursor, isbn):
    """Check if a book is currently checked out."""
    cursor.execute("""
        SELECT COUNT(*) as count
        FROM BOOK_LOANS
        WHERE isbn = ? AND date_in IS NULL
    """, (isbn,))
    result = cursor.fetchone()
    return result["count"] > 0 if result else False


@bp.post("/checkout")
def checkout():
    """Checkout a single book."""
    data = request.get_json(silent=True) or {}
    isbn = (data.get("isbn") or "").strip()
    borrower_card_no = (data.get("borrower_card_no") or data.get("card_id") or "").strip()
    
    if not isbn or not borrower_card_no:
        return jsonify({"error": "ISBN and borrower_card_no are required"}), 400
    
    conn = get_db()
    try:
        cursor = conn.cursor()
        
        # Verify book exists
        cursor.execute("SELECT isbn_primary FROM BOOK WHERE isbn_primary = ?", (isbn,))
        if not cursor.fetchone():
            return jsonify({"error": "Book not found"}), 404
        
        # Verify borrower exists
        cursor.execute("SELECT card_id FROM BORROWER WHERE card_id = ?", (borrower_card_no,))
        if not cursor.fetchone():
            return jsonify({"error": "Borrower not found"}), 404
        
        # Check if borrower has unpaid fines
        if has_unpaid_fines(cursor, borrower_card_no):
            return jsonify({"error": "Borrower has unpaid fines and cannot checkout books"}), 400
        
        # Check active loan count (max 3)
        active_count = get_active_loan_count(cursor, borrower_card_no)
        if active_count >= 3:
            return jsonify({"error": "Borrower has reached maximum of 3 active loans"}), 400
        
        # Check if book is already checked out
        if is_book_checked_out(cursor, isbn):
            return jsonify({"error": "Book is already checked out"}), 400
        
        # Create loan
        today = date.today().isoformat()
        due_date = (date.today() + timedelta(days=14)).isoformat()
        
        cursor.execute("""
            INSERT INTO BOOK_LOANS (isbn, card_id, date_out, due_date, date_in)
            VALUES (?, ?, ?, ?, NULL)
        """, (isbn, borrower_card_no, today, due_date))
        
        loan_id = cursor.lastrowid
        conn.commit()
        
        return jsonify({
            "loan_id": loan_id,
            "isbn": isbn,
            "card_no": borrower_card_no,
            "date_out": today,
            "due_date": due_date
        }), 201
        
    except Exception as e:
        conn.rollback()
        return jsonify({"error": "Database error", "details": str(e)}), 500
    finally:
        conn.close()


@bp.post("/checkout/batch")
def checkout_batch():
    """Checkout multiple books."""
    data = request.get_json(silent=True) or {}
    isbns = data.get("isbns", [])
    borrower_card_no = (data.get("borrower_card_no") or data.get("card_id") or "").strip()
    
    if not borrower_card_no:
        return jsonify({"error": "borrower_card_no is required"}), 400
    
    if not isbns or not isinstance(isbns, list):
        return jsonify({"error": "isbns must be a non-empty array"}), 400
    
    results = []
    conn = get_db()
    try:
        cursor = conn.cursor()
        
        # Verify borrower exists
        cursor.execute("SELECT card_id FROM BORROWER WHERE card_id = ?", (borrower_card_no,))
        if not cursor.fetchone():
            return jsonify({"error": "Borrower not found"}), 404
        
        # Check if borrower has unpaid fines (once for the batch)
        if has_unpaid_fines(cursor, borrower_card_no):
            return jsonify({"error": "Borrower has unpaid fines and cannot checkout books"}), 400
        
        # Process each ISBN
        for isbn in isbns:
            isbn = str(isbn).strip()
            if not isbn:
                results.append({"isbn": isbn, "status": "error", "error": "Empty ISBN"})
                continue
            
            try:
                # Verify book exists
                cursor.execute("SELECT isbn_primary FROM BOOK WHERE isbn_primary = ?", (isbn,))
                if not cursor.fetchone():
                    results.append({"isbn": isbn, "status": "error", "error": "Book not found"})
                    continue
                
                # Check active loan count
                active_count = get_active_loan_count(cursor, borrower_card_no)
                if active_count >= 3:
                    results.append({"isbn": isbn, "status": "error", "error": "Maximum active loans reached"})
                    continue
                
                # Check if book is already checked out
                if is_book_checked_out(cursor, isbn):
                    results.append({"isbn": isbn, "status": "error", "error": "Book already checked out"})
                    continue
                
                # Create loan
                today = date.today().isoformat()
                due_date = (date.today() + timedelta(days=14)).isoformat()
                
                cursor.execute("""
                    INSERT INTO BOOK_LOANS (isbn, card_id, date_out, due_date, date_in)
                    VALUES (?, ?, ?, ?, NULL)
                """, (isbn, borrower_card_no, today, due_date))
                
                loan_id = cursor.lastrowid
                conn.commit()
                
                results.append({
                    "isbn": isbn,
                    "status": "ok",
                    "loan_id": loan_id
                })
                
            except Exception as e:
                conn.rollback()
                results.append({"isbn": isbn, "status": "error", "error": str(e)})
        
        return jsonify(results), 200
        
    except Exception as e:
        conn.rollback()
        return jsonify({"error": "Database error", "details": str(e)}), 500
    finally:
        conn.close()


@bp.post("/checkin")
def checkin():
    """Check in a book by loan_id."""
    data = request.get_json(silent=True) or {}
    loan_id = data.get("loan_id")
    
    if loan_id is None:
        return jsonify({"error": "loan_id is required"}), 400
    
    try:
        loan_id = int(loan_id)
    except (ValueError, TypeError):
        return jsonify({"error": "loan_id must be a number"}), 400
    
    conn = get_db()
    try:
        cursor = conn.cursor()
        
        # Verify loan exists and is not already checked in
        cursor.execute("""
            SELECT loan_id, date_in FROM BOOK_LOANS WHERE loan_id = ?
        """, (loan_id,))
        loan = cursor.fetchone()
        
        if not loan:
            return jsonify({"error": "Loan not found"}), 404
        
        if loan["date_in"] is not None:
            return jsonify({"error": "Book is already checked in"}), 400
        
        # Update loan with checkin date
        today = date.today().isoformat()
        cursor.execute("""
            UPDATE BOOK_LOANS SET date_in = ? WHERE loan_id = ?
        """, (today, loan_id))
        
        conn.commit()
        
        return jsonify({
            "loan_id": loan_id,
            "date_in": today
        }), 200
        
    except Exception as e:
        conn.rollback()
        return jsonify({"error": "Database error", "details": str(e)}), 500
    finally:
        conn.close()


@bp.get("/checkin/search")
def checkin_search():
    """Search for loans to check in by ISBN, card_no, or borrower name."""
    isbn = request.args.get("isbn", "").strip()
    card_no = request.args.get("card_no", "").strip()
    borrower_name = request.args.get("borrower_name", "").strip()
    
    conn = get_db()
    try:
        cursor = conn.cursor()
        
        # Build dynamic query
        conditions = ["bl.date_in IS NULL"]  # Only show active loans
        params = []
        
        if isbn:
            conditions.append("bl.isbn LIKE ?")
            params.append(f"%{isbn}%")
        
        if card_no:
            conditions.append("bl.card_id LIKE ?")
            params.append(f"%{card_no}%")
        
        if borrower_name:
            conditions.append("LOWER(b.bname) LIKE LOWER(?)")
            params.append(f"%{borrower_name}%")
        
        sql = f"""
            SELECT 
                bl.loan_id,
                bl.isbn,
                bl.card_id,
                bl.date_out,
                bl.due_date,
                b.bname as borrower_name,
                book.title
            FROM BOOK_LOANS bl
            JOIN BORROWER b ON bl.card_id = b.card_id
            JOIN BOOK book ON bl.isbn = book.isbn_primary
            WHERE {' AND '.join(conditions)}
            ORDER BY bl.due_date
        """
        
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        
        results = []
        for row in rows:
            results.append({
                "loan_id": row["loan_id"],
                "isbn": row["isbn"],
                "card_id": row["card_id"],
                "borrower_name": row["borrower_name"],
                "title": row["title"],
                "date_out": row["date_out"],
                "due_date": row["due_date"]
            })
        
        return jsonify(results), 200
        
    except Exception as e:
        return jsonify({"error": "Database error", "details": str(e)}), 500
    finally:
        conn.close()
