from flask import Blueprint, jsonify, request
from db import get_db

bp = Blueprint("search", __name__, url_prefix="/api")


@bp.get("/search")
def search():
    # TODO: implement using SQLite with substring match on isbn/title/authors.
    # Expect query param: q
    # SQLite uses ? placeholders (not %s)
    # Use LIKE with LOWER() for case-insensitive search
    # Return array of: isbn, title, authors (array), checked_out (bool), borrower_id (string|null)
    return jsonify({"error": "not implemented"}), 501

