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
