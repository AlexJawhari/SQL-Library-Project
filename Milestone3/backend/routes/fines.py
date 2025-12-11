from flask import Blueprint, jsonify, request
from db import get_db
from datetime import date

bp = Blueprint("fines", __name__, url_prefix="/api")


@bp.post("/fines/refresh")
def fines_refresh():
    """Refresh fines for all late books."""
    conn = get_db()
    try:
        cursor = conn.cursor()
        today = date.today().isoformat()
        refreshed_count = 0
        
        # Get all loans that are late (due_date < today or (date_in > due_date))
        cursor.execute("""
            SELECT loan_id, due_date, date_in
            FROM BOOK_LOANS
            WHERE (date_in IS NULL AND due_date < ?) OR (date_in IS NOT NULL AND date_in > due_date)
        """, (today,))
        
        loans = cursor.fetchall()
        
        for loan in loans:
            loan_id = loan["loan_id"]
            due_date = loan["due_date"]
            date_in = loan["date_in"]
            
            # Calculate days late
            if date_in:
                # Book has been returned - calculate from date_in
                due = date.fromisoformat(due_date)
                returned = date.fromisoformat(date_in)
                days_late = (returned - due).days
            else:
                # Book still out - calculate from today
                due = date.fromisoformat(due_date)
                today_date = date.today()
                days_late = (today_date - due).days
            
            if days_late > 0:
                fine_amt = days_late * 0.25
                
                # Check if fine already exists
                cursor.execute("SELECT paid FROM FINES WHERE loan_id = ?", (loan_id,))
                existing = cursor.fetchone()
                
                if existing:
                    # Fine exists - only update if not paid
                    if existing["paid"] == 0:
                        cursor.execute("""
                            UPDATE FINES SET fine_amt = ? WHERE loan_id = ?
                        """, (fine_amt, loan_id))
                        refreshed_count += 1
                else:
                    # Create new fine
                    cursor.execute("""
                        INSERT INTO FINES (loan_id, fine_amt, paid)
                        VALUES (?, ?, 0)
                    """, (loan_id, fine_amt))
                    refreshed_count += 1
        
        conn.commit()
        return jsonify({"refreshed": refreshed_count}), 200
        
    except Exception as e:
        conn.rollback()
        return jsonify({"error": "Database error", "details": str(e)}), 500
    finally:
        conn.close()


@bp.get("/fines")
def fines_list():
    """List fines grouped by borrower card_no."""
    conn = get_db()
    try:
        cursor = conn.cursor()
        card_no = request.args.get("card_no", "").strip()
        show_paid = request.args.get("show_paid", "false").lower() == "true"
        
        # Build query
        if card_no:
            if show_paid:
                cursor.execute("""
                    SELECT 
                        bl.card_id as card_no,
                        SUM(f.fine_amt) AS total_fines,
                        CASE WHEN SUM(CASE WHEN f.paid = 0 THEN 1 ELSE 0 END) > 0 THEN 0 ELSE 1 END as paid
                    FROM FINES f
                    JOIN BOOK_LOANS bl ON f.loan_id = bl.loan_id
                    WHERE bl.card_id = ?
                    GROUP BY bl.card_id
                """, (card_no,))
            else:
                cursor.execute("""
                    SELECT 
                        bl.card_id as card_no,
                        SUM(f.fine_amt) AS total_fines,
                        0 as paid
                    FROM FINES f
                    JOIN BOOK_LOANS bl ON f.loan_id = bl.loan_id
                    WHERE bl.card_id = ? AND f.paid = 0
                    GROUP BY bl.card_id
                """, (card_no,))
        else:
            if show_paid:
                cursor.execute("""
                    SELECT 
                        bl.card_id as card_no,
                        SUM(f.fine_amt) AS total_fines,
                        CASE WHEN SUM(CASE WHEN f.paid = 0 THEN 1 ELSE 0 END) > 0 THEN 0 ELSE 1 END as paid
                    FROM FINES f
                    JOIN BOOK_LOANS bl ON f.loan_id = bl.loan_id
                    GROUP BY bl.card_id
                """)
            else:
                cursor.execute("""
                    SELECT 
                        bl.card_id as card_no,
                        SUM(f.fine_amt) AS total_fines,
                        0 as paid
                    FROM FINES f
                    JOIN BOOK_LOANS bl ON f.loan_id = bl.loan_id
                    WHERE f.paid = 0
                    GROUP BY bl.card_id
                """)
        
        rows = cursor.fetchall()
        results = []
        for row in rows:
            results.append({
                "card_no": row["card_no"],
                "total_fines": round(row["total_fines"], 2),
                "paid": bool(row["paid"])
            })
        
        return jsonify(results), 200
        
    except Exception as e:
        return jsonify({"error": "Database error", "details": str(e)}), 500
    finally:
        conn.close()


@bp.post("/fines/pay")
def fines_pay():
    """Pay all fines for a borrower (only if all loans are returned)."""
    data = request.get_json(silent=True) or {}
    card_no = (data.get("card_no") or "").strip()
    
    if not card_no:
        return jsonify({"error": "Missing card_no"}), 400
    
    conn = get_db()
    try:
        cursor = conn.cursor()
        
        # Verify borrower exists
        cursor.execute("SELECT card_id FROM BORROWER WHERE card_id = ?", (card_no,))
        if not cursor.fetchone():
            return jsonify({"error": "Borrower not found"}), 404
        
        # Check if borrower has any unreturned books
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM BOOK_LOANS
            WHERE card_id = ? AND date_in IS NULL
        """, (card_no,))
        result = cursor.fetchone()
        if result and result["count"] > 0:
            return jsonify({"error": "Cannot pay fines while borrower has unreturned books"}), 400
        
        # Update all unpaid fines for this borrower to paid
        cursor.execute("""
            UPDATE FINES
            SET paid = 1
            WHERE paid = 0 AND loan_id IN (
                SELECT loan_id FROM BOOK_LOANS WHERE card_id = ?
            )
        """, (card_no,))
        
        paid_count = cursor.rowcount
        conn.commit()
        
        return jsonify({"paid": paid_count}), 200
        
    except Exception as e:
        conn.rollback()
        return jsonify({"error": "Database error", "details": str(e)}), 500
    finally:
        conn.close()
