from flask import (
    Blueprint, request, jsonify
)

from flaskr.db import get_db

from werkzeug.exceptions import abort

import re


bp = Blueprint('products', __name__, url_prefix='/products/')

def product_exists(id):
    return get_db().execute(
        'SELECT * FROM Product WHERE ProductID = ?',
        (id,)
    ).fetchone() is not None
    


@bp.route('/', methods=('GET',))
def index():
    response = get_db().execute(
        "SELECT * FROM Product"
    ).fetchall()

    return jsonify([dict(row) for row in response])


@bp.route('/', methods=('POST',))
def create():
    name = request.form['ProductName']
    price = request.form['ProductPrice']
    stock = request.form['ProductStock']
    minstock = request.form['ProductMinStock']


    if not name:
        abort(400, 'Name is required.')
    elif not price:
        abort(400, 'Price is required.')
    elif not re.match(r'^\d+(\.\d+)?$', price):
        abort(400, 'Price need to be a number.')    
    elif not stock:
        abort(400, 'Stock is required.')
    elif not re.match(r'^\d+$', stock):
        abort(400, 'Stock need to be a integer.')
    elif not minstock:
        abort(400, 'Min stock is required.')
    elif not re.match(r'^\d+$', minstock):
        abort(400, 'Min stock need to be a integer.')

    try:
        db = get_db()
        db.execute(
            'INSERT INTO Product (ProductName, ProductPrice, ProductStock, ProductMinStock) VALUES (?, ?, ?, ?)',
            (name, price, stock, minstock)
        )
        db.commit()
    except db.IntegrityError:
        abort(400, b'Already exists.')     

    return ''


@bp.route('/<int:id>/', methods=('GET',))
def get(id):
    if not product_exists(id):
        abort(404, 'Not Found')

    response = get_db().execute(
        'SELECT * FROM Product WHERE ProductID = ?',
        (id,)
    ).fetchone()

    return jsonify(dict(response))


@bp.route('/<int:id>/', methods=('DELETE',))
def delete(id):
    if not product_exists(id):
        abort(404, 'Not Found')

    db = get_db()
    db.execute(
        'DELETE FROM Product WHERE ProductID = ?',
        (id,)
    )
    db.commit()

    return ''


@bp.route('/<int:id>/price/', methods=('PUT',))
def update_price(id):
    if not product_exists(id):
        abort(404, 'Not Found')

    price = request.form['ProductPrice']

    if not price:
        abort(400, 'Price is required.')
    elif not re.match(r'^\d+(\.\d+)?$', price):
        abort(400, 'Price need to be a number.')

    db = get_db()
    db.execute(
        'UPDATE Product SET ProductPrice = ? WHERE ProductID = ?',
        (price, id)
    )
    db.commit()

    return ''


@bp.route('/<int:id>/minstock/', methods=('PUT',))
def update_minstock(id):
    if not product_exists(id):
        abort(404, 'Not Found')
        
    minstock = request.form['ProductMinStock']

    if not minstock:
        abort(400, 'Min stock is required.')
    elif not re.match(r'^\d+$', minstock):
        abort(400, 'Min stock need to be a integer.')

    db = get_db()
    db.execute(
        'UPDATE Product SET ProductMinStock = ? WHERE ProductID = ?',
        (minstock, id)
    )
    db.commit()

    return ''
