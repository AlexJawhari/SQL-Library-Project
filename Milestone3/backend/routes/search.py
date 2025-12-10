from flask import Blueprint, jsonify, request
from db import get_db

bp = Blueprint("search", __name__, url_prefix="/api")


@bp.get("/search")
def search():
    # TODO: implement using MySQL with substring match on isbn/title/authors.
    # Expect query param: q
    return jsonify({"error": "not implemented"}), 501

