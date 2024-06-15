from flask import (
    Blueprint, request, jsonify
)

from flaskr.db import get_db

bp = Blueprint('notes', __name__, url_prefix='/notes/')

@bp.route('/', methods=('GET',))
def index():
    response = get_db().execute(
        "SELECT * FROM Note"
    ).fetchall()

    return jsonify([dict(row) for row in response])

