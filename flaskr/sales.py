from flask import (
    Blueprint, request, jsonify
)

from flaskr.db import get_db

from werkzeug.exceptions import abort

import re


bp = Blueprint('sales', __name__, url_prefix='/sales/')

def sale_exists(id):
    return get_db().execute(
        'SELECT * FROM Sale WHERE SaleID = ?',
        (id,)
    ).fetchone() is not None


@bp.route('/', methods=('GET',))
def index():
    response = get_db().execute(
        "SELECT * FROM Sale"
    ).fetchall()

    return jsonify([dict(row) for row in response])


@bp.route('/', methods=('POST',))
def create():
    try:
        db = get_db()
        db.execute(
            'INSERT INTO Sale (SaleTotal) VALUES (?)',
            ('0')
        )
        db.commit()
    except db.IntegrityError:
        pass

    return ''


@bp.route('/<int:sale_id>/total/', methods=('GET',))
def get_sale_total(sale_id):
    if not sale_exists(sale_id):
        abort(404, 'Not Found')

    response = get_db().execute(
        'SELECT SaleTotal FROM Sale WHERE SaleID = ?',
        (sale_id,)
    ).fetchone()

    return jsonify(dict(response))


@bp.route('/<int:sale_id>/', methods=('DELETE',))
def delete_sale(sale_id):
    if not sale_exists(sale_id):
        abort(404, 'Not Found')

    try:
        db = get_db()
        db.execute('PRAGMA foreign_keys = ON')
        db.execute(
            'DELETE FROM Sale WHERE SaleID = ?',
            (sale_id,)
        )
        db.commit()
    except db.InternalError:
        pass

    return ''


@bp.route('/<int:sale_id>/products/', methods=('GET',))
def get_products(sale_id):
    if not sale_exists(sale_id):
        abort(404, 'Not Found')

    response = get_db().execute(
        'SELECT * FROM SaleProduct WHERE SaleID = ?',
        (sale_id,)
    ).fetchall()

    return jsonify([dict(row) for row in response])


@bp.route('/<int:sale_id>/products/', methods=('POST',))
def add_product(sale_id):
    if not sale_exists(sale_id):
        abort(404, 'Not Found')

    product_id = request.form['ProductID']
    price = request.form['Price']
    amount = request.form['Amount']

    if not product_id:
        abort(400, 'ProductID is required.')
    elif not re.match(r'^\d+$', product_id):
        abort(400, 'ProductID need to be a integer.')
    elif not price:
        abort(400, 'Price is required.')
    elif not re.match(r'^\d+(\.\d+)?$', price):
        abort(400, 'Price need to be a number.')
    if not amount:
        abort(400, 'Amount is required.')
    elif not re.match(r'^\d+$', amount):
        abort(400, 'Amount need to be a integer.')

    try:
        db = get_db()
        db.execute(
            'INSERT INTO SaleProduct (SaleID, ProductID, Price, Amount) VALUES (?, ?, ?, ?)',
            (sale_id, product_id, price, amount)
        )
        db.commit()
    except db.IntegrityError:
        abort(400, 'Already exists.')

    return ''


@bp.route('/<int:sale_id>/products/<int:product_id>/', methods=('DELETE',))
def remove_product(sale_id, product_id):
    db = get_db()

    exists = db.execute(
        'SELECT * FROM SaleProduct WHERE SaleID = ? AND ProductID = ?',
        (sale_id, product_id)
    ).fetchone() is not None

    if not exists:
        abort(404, 'Not Found')

    db.execute(
        'DELETE FROM SaleProduct WHERE SaleID = ? AND ProductID = ?',
        (sale_id, product_id)
    )
    db.commit()

    return ''