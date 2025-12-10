from flask import Blueprint, jsonify, request
from db import get_db

bp = Blueprint("fines", __name__, url_prefix="/api")


@bp.post("/fines/refresh")
def fines_refresh():
    # TODO: compute fines per rules; keep paid fines unchanged.
    return jsonify({"error": "not implemented"}), 501


@bp.get("/fines")
def fines_list():
    # TODO: sum fines grouped by card_no, filter by query param card_no.
    return jsonify({"error": "not implemented"}), 501


@bp.post("/fines/pay")
def fines_pay():
    # TODO: allow pay only if all loans returned.
    return jsonify({"error": "not implemented"}), 501

