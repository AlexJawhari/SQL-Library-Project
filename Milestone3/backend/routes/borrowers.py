from flask import Blueprint, jsonify, request
from db import get_db
import re

bp = Blueprint("borrowers", __name__, url_prefix="/api")


def generate_new_card_id(cur):
    cur.execute(
        """
        SELECT MAX(CAST(SUBSTR(card_id, 3) AS INTEGER)) AS max_value
        FROM BORROWER
        WHERE card_id LIKE 'ID%'
        """
    )
    row = cur.fetchone()
    num = row["max_value"] if row["max_value"] is not None else 0
    return f"ID{num + 1:06d}"


@bp.post("/borrowers")
def create_borrower():
    data = request.get_json(silent=True) or {}

    ssn = (data.get("ssn") or "").strip()
    bname = (data.get("bname") or "").strip()
    address = (data.get("address") or "").strip()
    phone = (data.get("phone") or "").strip()

    if not ssn or not bname or not address:
        return jsonify({"error": "Missing required fields"}), 400

    digits = re.sub(r"\D", "", ssn)
    if len(digits) != 9:
        return jsonify({"error": "SSN must contain 9 digits"}), 400
    ssn_norm = f"{digits[0:3]}-{digits[3:5]}-{digits[5:9]}"

    conn = get_db()
    try:
        cur = conn.cursor()

        cur.execute("SELECT card_id FROM BORROWER WHERE ssn = ?", (ssn_norm,))
        existing = cur.fetchone()
        if existing:
            return (
                jsonify(
                    {
                        "error": "Borrower exists",
                        "card_id": existing["card_id"],
                    }
                ),
                409,
            )

        new_id = generate_new_card_id(cur)

        cur.execute(
            """
            INSERT INTO BORROWER (card_id, ssn, bname, address, phone)
            VALUES (?, ?, ?, ?, ?)
            """,
            (new_id, ssn_norm, bname, address, phone or None),
        )

        conn.commit()

        return (
            jsonify(
                {
                    "card_id": new_id,
                    "ssn": ssn_norm,
                    "bname": bname,
                    "address": address,
                    "phone": phone or None,
                }
            ),
            201,
        )

    except Exception as e:
        conn.rollback()
        return jsonify({"error": "Database error", "details": str(e)}), 500
    finally:
        conn.close()


@bp.route("/borrowers/<card_id>", methods=["DELETE"])
def delete_borrower(card_id):
    """Delete a borrower if they have no active loans or unpaid fines."""
    conn = get_db()
    try:
        cursor = conn.cursor()
        
        # Verify borrower exists
        cursor.execute("SELECT card_id FROM BORROWER WHERE card_id = ?", (card_id,))
        if not cursor.fetchone():
            return jsonify({"error": "Borrower not found"}), 404
        
        # Check for active loans
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM BOOK_LOANS
            WHERE card_id = ? AND date_in IS NULL
        """, (card_id,))
        result = cursor.fetchone()
        if result and result["count"] > 0:
            return jsonify({
                "error": "Cannot delete borrower with active loans",
                "active_loans": result["count"]
            }), 400
        
        # Check for unpaid fines
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM FINES f
            JOIN BOOK_LOANS bl ON f.loan_id = bl.loan_id
            WHERE bl.card_id = ? AND f.paid = 0
        """, (card_id,))
        result = cursor.fetchone()
        if result and result["count"] > 0:
            return jsonify({
                "error": "Cannot delete borrower with unpaid fines",
                "unpaid_fines_count": result["count"]
            }), 400
        
        # Delete all fines associated with this borrower's loans first
        cursor.execute("""
            DELETE FROM FINES
            WHERE loan_id IN (
                SELECT loan_id FROM BOOK_LOANS WHERE card_id = ?
            )
        """, (card_id,))
        
        # Delete all loans for this borrower
        cursor.execute("DELETE FROM BOOK_LOANS WHERE card_id = ?", (card_id,))
        
        # Delete the borrower
        cursor.execute("DELETE FROM BORROWER WHERE card_id = ?", (card_id,))
        
        conn.commit()
        
        return jsonify({
            "message": "Borrower deleted successfully",
            "card_id": card_id
        }), 200
        
    except Exception as e:
        conn.rollback()
        return jsonify({"error": "Database error", "details": str(e)}), 500
    finally:
        conn.close()