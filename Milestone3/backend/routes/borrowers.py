from flask import Blueprint, jsonify, request
from db import get_db

bp = Blueprint("borrowers", __name__, url_prefix="/api")


@bp.post("/borrowers")
def create_borrower():
    # TODO: enforce SSN uniqueness, required fields, generate ID######.
    return jsonify({"error": "not implemented"}), 501

