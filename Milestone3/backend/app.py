from flask import Flask, request, jsonify
from pathlib import Path
import pymysql
# Placeholder backend for teammates to implement. Uses MySQL connection helpers.

app = Flask(__name__)

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

# MySQL connection settings (teammates: fill these in)
MYSQL_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "library_demo",
    "cursorclass": pymysql.cursors.DictCursor,
    "charset": "utf8mb4",
    "autocommit": True,
}


def get_db():
    # Teammates can swap to a pooled connection if desired.
    return pymysql.connect(**MYSQL_CONFIG)


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/search")
def search():
    # TODO: implement using MySQL query with substring match on isbn/title/authors.
    # Expect query param: q
    return jsonify({"error": "not implemented"}), 501


@app.post("/api/checkout")
def checkout():
    # TODO: enforce rules (3-loan limit, already out, fines block).
    # Body: { isbn, borrower_card_no }
    return jsonify({"error": "not implemented"}), 501


@app.post("/api/checkout/batch")
def checkout_batch():
    # TODO: loop over isbns, reuse checkout logic.
    return jsonify({"error": "not implemented"}), 501


@app.post("/api/checkin")
def checkin():
    # TODO: set date_in = today for given loan_id.
    return jsonify({"error": "not implemented"}), 501


@app.post("/api/borrowers")
def create_borrower():
    # TODO: enforce SSN uniqueness, required fields, generate ID######.
    return jsonify({"error": "not implemented"}), 501


@app.post("/api/fines/refresh")
def fines_refresh():
    # TODO: compute fines per rules; keep paid fines unchanged.
    return jsonify({"error": "not implemented"}), 501


@app.get("/api/fines")
def fines_list():
    # TODO: sum fines grouped by card_no, filter by query param card_no.
    return jsonify({"error": "not implemented"}), 501


@app.post("/api/fines/pay")
def fines_pay():
    # TODO: allow pay only if all loans returned.
    return jsonify({"error": "not implemented"}), 501


def init_db_schema_and_import():
    """
    TODO (teammates):
    - Create tables in MySQL (based on Milestone2 SQL; adjust types for MySQL).
    - Import CSVs from DATA_DIR using LOAD DATA INFILE or a small Python importer.
    """
    pass


if __name__ == "__main__":
    # Run with: python app.py
    # Add debug=True for development if desired.
    app.run(host="127.0.0.1", port=5000)

