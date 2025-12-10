from flask import Blueprint, jsonify, request
from db import get_db

bp = Blueprint("fines", __name__, url_prefix="/api")

#1. Refresh fines using the stored procedure
@bp.post("/fines/refresh")
def fines_refresh():
    db = get_db()
    cur = db.cursor()
    try:
        cur.callproc("refresh_fines")  #call the SQLl procedure
        db.commit()
        retunr jsonify({"status": "ok", "message": "Fines refreshed"})
    finally:
        cur.close()
        db.close()

  # 2. List fines grouped by borrower, unpaid only
@bp.get("/fines")
def fines_list():
    db = get_db()
    cur = db.cursor()
    card_no = request.args.get("card_no")

    if card_no:
        cur.execute("""
        SELECT bl.card, SUM(f.fine_amt) AS total_fines
            FROM fines f
            JOIN book_loans bl ON f.loan_id = bl.loan_id
            WHERE f.paid = 0 AND bl.card_id = %s
            GROUP BY bl.card_id;
        """, (card_no,))
    else:
        cur.execute("""
            SELECT bl.card_id, SUM(f.fine_amt) AS total_fines
            FROM fines f
            JOIN book_loans bl ON f.loan_id = bl.loan_id
            WHERE f.paid = 0
            GROUP BY bl.card_id;
        """)
    results = cur.fetchall()
    cur.close()
    db.close()
    return jsonify(results)
        
   
    #3 pay fines using the stored procedure
@bp.post("/fines/pay")
def fines_pay():
    db = get_db.cursor()
    cur = db.cursor()
    card_no = request.json.get("card_no")
    if not card_no:
        return jsonify({"error": "Missing card_no"}), 400
    try:
        cur.callproc("pay_all_fines", [card_no]) #call the sql procedure
        db.commit()
    except Exception as err:
        #if the procedure raised SIGNAL unreturned book, catch it
        return jsonify({"status": "error", "card_no": card_no, "message" : str(err)}), 400
    finally:
        cur.close()
        db.close()
    return jsonify({"status": "paid", "card_no": card_no})
    
