from flask import Blueprint, jsonify, request
from db import get_db

bp = Blueprint("loans", __name__, url_prefix="/api")


@bp.post("/checkout")
def checkout():
    # TODO: enforce rules (3-loan limit, already out, fines block).
    # Body: { isbn, borrower_card_no }
    return jsonify({"error": "not implemented"}), 501


@bp.post("/checkout/batch")
def checkout_batch():
    # TODO: loop over isbns, reuse checkout logic.
    return jsonify({"error": "not implemented"}), 501


@bp.post("/checkin")
def checkin():
    # TODO: set date_in = today for given loan_id.
    return jsonify({"error": "not implemented"}), 501

