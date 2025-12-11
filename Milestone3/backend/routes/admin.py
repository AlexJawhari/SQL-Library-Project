from flask import Blueprint, jsonify, request
from db import get_db

bp = Blueprint("admin", __name__, url_prefix="/api/admin")


@bp.route("/borrowers", methods=["GET"])
def get_all_borrowers():
    """Get all borrowers with loan and fine counts."""
    conn = get_db()
    try:
        cursor = conn.cursor()
        search = request.args.get("search", "").strip()
        
        # Build query
        if search:
            sql = """
                SELECT 
                    b.card_id,
                    b.ssn,
                    b.bname,
                    b.address,
                    b.phone,
                    COALESCE(loan_counts.active_loans, 0) as active_loans,
                    COALESCE(fine_totals.unpaid_fines, 0) as unpaid_fines
                FROM BORROWER b
                LEFT JOIN (
                    SELECT card_id, COUNT(*) as active_loans
                    FROM BOOK_LOANS
                    WHERE date_in IS NULL
                    GROUP BY card_id
                ) loan_counts ON b.card_id = loan_counts.card_id
                LEFT JOIN (
                    SELECT bl.card_id, SUM(f.fine_amt) as unpaid_fines
                    FROM FINES f
                    JOIN BOOK_LOANS bl ON f.loan_id = bl.loan_id
                    WHERE f.paid = 0
                    GROUP BY bl.card_id
                ) fine_totals ON b.card_id = fine_totals.card_id
                WHERE 
                    LOWER(b.card_id) LIKE LOWER(?) OR
                    LOWER(b.bname) LIKE LOWER(?) OR
                    LOWER(b.ssn) LIKE LOWER(?)
                ORDER BY b.card_id
            """
            search_term = f"%{search}%"
            cursor.execute(sql, (search_term, search_term, search_term))
        else:
            sql = """
                SELECT 
                    b.card_id,
                    b.ssn,
                    b.bname,
                    b.address,
                    b.phone,
                    COALESCE(loan_counts.active_loans, 0) as active_loans,
                    COALESCE(fine_totals.unpaid_fines, 0) as unpaid_fines
                FROM BORROWER b
                LEFT JOIN (
                    SELECT card_id, COUNT(*) as active_loans
                    FROM BOOK_LOANS
                    WHERE date_in IS NULL
                    GROUP BY card_id
                ) loan_counts ON b.card_id = loan_counts.card_id
                LEFT JOIN (
                    SELECT bl.card_id, SUM(f.fine_amt) as unpaid_fines
                    FROM FINES f
                    JOIN BOOK_LOANS bl ON f.loan_id = bl.loan_id
                    WHERE f.paid = 0
                    GROUP BY bl.card_id
                ) fine_totals ON b.card_id = fine_totals.card_id
                ORDER BY b.card_id
            """
            cursor.execute(sql)
        
        rows = cursor.fetchall()
        results = []
        for row in rows:
            results.append({
                "card_id": row["card_id"],
                "ssn": row["ssn"],
                "bname": row["bname"],
                "address": row["address"],
                "phone": row["phone"],
                "active_loans": row["active_loans"],
                "unpaid_fines": round(row["unpaid_fines"], 2)
            })
        
        return jsonify(results), 200
        
    except Exception as e:
        return jsonify({"error": "Database error", "details": str(e)}), 500
    finally:
        conn.close()


@bp.route("/loans", methods=["GET"])
def get_all_loans():
    """Get all loans with optional filtering."""
    conn = get_db()
    try:
        cursor = conn.cursor()
        filter_type = request.args.get("filter", "all")
        search = request.args.get("search", "").strip()
        
        # Build conditions
        conditions = []
        params = []
        
        if filter_type == "active":
            conditions.append("bl.date_in IS NULL")
        elif filter_type == "returned":
            conditions.append("bl.date_in IS NOT NULL")
        
        if search:
            conditions.append("""
                (LOWER(bl.isbn) LIKE LOWER(?) OR
                 LOWER(bl.card_id) LIKE LOWER(?) OR
                 LOWER(b.bname) LIKE LOWER(?))
            """)
            search_term = f"%{search}%"
            params.extend([search_term, search_term, search_term])
        
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        
        sql = f"""
            SELECT 
                bl.loan_id,
                bl.isbn,
                bl.card_id,
                bl.date_out,
                bl.due_date,
                bl.date_in,
                b.bname as borrower_name,
                book.title
            FROM BOOK_LOANS bl
            JOIN BORROWER b ON bl.card_id = b.card_id
            LEFT JOIN BOOK book ON bl.isbn = book.isbn_primary
            WHERE {where_clause}
            ORDER BY bl.date_out DESC
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
                "due_date": row["due_date"],
                "date_in": row["date_in"]
            })
        
        return jsonify(results), 200
        
    except Exception as e:
        return jsonify({"error": "Database error", "details": str(e)}), 500
    finally:
        conn.close()


@bp.route("/fines", methods=["GET"])
def get_all_fines():
    """Get all fines with detailed information."""
    conn = get_db()
    try:
        cursor = conn.cursor()
        filter_type = request.args.get("filter", "unpaid")
        search = request.args.get("search", "").strip()
        
        # Build conditions
        conditions = []
        params = []
        
        if filter_type == "unpaid":
            conditions.append("f.paid = 0")
        elif filter_type == "paid":
            conditions.append("f.paid = 1")
        
        if search:
            conditions.append("""
                (LOWER(bl.card_id) LIKE LOWER(?) OR
                 LOWER(b.bname) LIKE LOWER(?))
            """)
            search_term = f"%{search}%"
            params.extend([search_term, search_term])
        
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        
        sql = f"""
            SELECT 
                f.loan_id,
                f.fine_amt,
                f.paid,
                bl.card_id,
                bl.isbn,
                bl.due_date,
                bl.date_in,
                b.bname as borrower_name,
                book.title,
                CASE
                    WHEN bl.date_in IS NOT NULL THEN
                        CAST((julianday(bl.date_in) - julianday(bl.due_date)) AS INTEGER)
                    ELSE
                        CAST((julianday('now') - julianday(bl.due_date)) AS INTEGER)
                END as days_late
            FROM FINES f
            JOIN BOOK_LOANS bl ON f.loan_id = bl.loan_id
            JOIN BORROWER b ON bl.card_id = b.card_id
            LEFT JOIN BOOK book ON bl.isbn = book.isbn_primary
            WHERE {where_clause}
            ORDER BY f.paid, bl.due_date DESC
        """
        
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        
        results = []
        for row in rows:
            results.append({
                "loan_id": row["loan_id"],
                "card_id": row["card_id"],
                "borrower_name": row["borrower_name"],
                "isbn": row["isbn"],
                "title": row["title"],
                "due_date": row["due_date"],
                "date_in": row["date_in"],
                "days_late": max(0, row["days_late"] or 0),
                "fine_amt": round(row["fine_amt"], 2),
                "paid": bool(row["paid"])
            })
        
        return jsonify(results), 200
        
    except Exception as e:
        return jsonify({"error": "Database error", "details": str(e)}), 500
    finally:
        conn.close()


@bp.route("/stats", methods=["GET"])
def get_stats():
    """Get system statistics."""
    conn = get_db()
    try:
        cursor = conn.cursor()
        
        # Count books
        cursor.execute("SELECT COUNT(*) as count FROM BOOK")
        book_count = cursor.fetchone()["count"]
        
        return jsonify({
            "count": book_count
        }), 200
        
    except Exception as e:
        return jsonify({"error": "Database error", "details": str(e)}), 500
    finally:
        conn.close()


@bp.route("/fines/apply", methods=["POST"])
def apply_fine():
    """Manually apply a fine to a loan (for testing purposes)."""
    conn = get_db()
    try:
        data = request.get_json()
        loan_id = data.get("loan_id")
        fine_amount = data.get("fine_amount")  # Optional: custom amount
        days_late = data.get("days_late")  # Optional: custom days late
        
        if not loan_id:
            return jsonify({"error": "loan_id is required"}), 400
        
        cursor = conn.cursor()
        
        # Verify loan exists
        cursor.execute("""
            SELECT loan_id, due_date, date_in, card_id
            FROM BOOK_LOANS
            WHERE loan_id = ?
        """, (loan_id,))
        loan = cursor.fetchone()
        
        if not loan:
            return jsonify({"error": "Loan not found"}), 404
        
        # Calculate fine amount
        if fine_amount is not None:
            # Use provided fine amount
            fine_amt = float(fine_amount)
        elif days_late is not None:
            # Calculate from provided days late
            fine_amt = float(days_late) * 0.25
        else:
            # Calculate from actual due date
            from datetime import date
            due_date = date.fromisoformat(loan["due_date"])
            if loan["date_in"]:
                returned = date.fromisoformat(loan["date_in"])
                days = (returned - due_date).days
            else:
                today = date.today()
                days = (today - due_date).days
            
            if days <= 0:
                return jsonify({"error": "Loan is not late. Cannot apply fine."}), 400
            
            fine_amt = days * 0.25
        
        if fine_amt <= 0:
            return jsonify({"error": "Fine amount must be greater than 0"}), 400
        
        # Check if fine already exists
        cursor.execute("SELECT paid, fine_amt FROM FINES WHERE loan_id = ?", (loan_id,))
        existing = cursor.fetchone()
        
        if existing:
            if existing["paid"] == 1:
                return jsonify({"error": "Fine already exists and is paid. Cannot modify."}), 400
            # Update existing fine
            cursor.execute("""
                UPDATE FINES SET fine_amt = ? WHERE loan_id = ?
            """, (fine_amt, loan_id))
            action = "updated"
        else:
            # Create new fine
            cursor.execute("""
                INSERT INTO FINES (loan_id, fine_amt, paid)
                VALUES (?, ?, 0)
            """, (loan_id, fine_amt))
            action = "created"
        
        conn.commit()
        
        return jsonify({
            "success": True,
            "message": f"Fine {action} successfully",
            "loan_id": loan_id,
            "fine_amount": round(fine_amt, 2),
            "card_id": loan["card_id"]
        }), 200
        
    except ValueError as e:
        return jsonify({"error": "Invalid fine amount or days late", "details": str(e)}), 400
    except Exception as e:
        conn.rollback()
        return jsonify({"error": "Database error", "details": str(e)}), 500
    finally:
        conn.close()

