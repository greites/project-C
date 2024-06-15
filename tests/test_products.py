import pytest

from flaskr.db import get_db

@pytest.mark.parametrize('path', (
    '/products/',
    '/products/1/'
))
def test_get(client, path):
    response = client.get(path)

    assert response.status_code == 200
    assert b'ProductID' in response.data

    assert client.get('/products/3/').status_code == 404


def test_create(client, app):
    data = {
        'ProductName': 'Apple',
        'ProductPrice': 1.99,
        'ProductStock': 50,
        'ProductMinStock': 30
    }

    client.post('/products/', data=data)
    
    with app.app_context():
        assert get_db().execute(
            'SELECT * FROM Product WHERE ProductName = "Apple"'
        ).fetchone() is not None


@pytest.mark.parametrize(('name', 'price', 'stock', 'minstock', 'message'),(
    ('', '', '', '', b'Name is required.'),
    ('a', '', '', '', b'Price is required.'),
    ('a', 'a', '', '', b'Price need to be a number.'),
    ('a', '1', '', '', b'Stock is required.'),
    ('a', '1', 'a', '', b'Stock need to be a integer.'),
    ('a', '1', '1', '', b'Min stock is required.'),
    ('a', '1', '1', 'a', b'Min stock need to be a integer.'),
    ('Orange', '1', '1', '1', b'Already exists.'),                    
))
def test_create_validade_input(client, name, price, stock, minstock, message):
    data = {
        'ProductName': name,
        'ProductPrice': price,
        'ProductStock': stock,
        'ProductMinStock': minstock,
    }
    
    response = client.post('/products/', data=data)

    assert message in response.data
    assert response.status_code == 400


def test_delete(client, app):
    client.delete('/products/1/')

    assert client.delete('/products/3/').status_code == 404

    with app.app_context():
        assert get_db().execute(
            'SELECT * FROM Product WHERE ProductID = 1'
        ).fetchone() is None


def test_update_price(client, app):
    data = {
        'ProductPrice': '1.03'
    }

    client.put('/products/1/price/', data=data)

    assert client.put('/products/3/price/').status_code == 404

    with app.app_context():
        assert get_db().execute(
            'SELECT * FROM Product WHERE ProductID = 1'
        ).fetchone()['ProductPrice'] == 1.03


@pytest.mark.parametrize(('price', 'message'), (
    ('', b'Price is required.'),
    ('a', b'Price need to be a number.'),
))
def test_update_price_validade_input(client, price, message):
    response = client.put('/products/1/price/', data={'ProductPrice': price})
    assert message in response.data
    assert response.status_code == 400


def test_update_minstock(client, app):
    data = {
        'ProductMinStock': '15'
    }

    client.put('/products/1/minstock/', data=data)

    assert client.put('/products/3/minstock/').status_code == 404

    with app.app_context():
        assert get_db().execute(
            'SELECT * FROM Product WHERE ProductID = 1'
        ).fetchone()['ProductMinStock'] == 15


@pytest.mark.parametrize(('minstock', 'message'), (
    ('', b'Min stock is required.'),
    ('a', b'Min stock need to be a integer.'),
))
def test_update_minstock_validade_input(client, minstock, message):
    response = client.put('/products/1/minstock/', data={'ProductMinStock': minstock})
    assert message in response.data
    assert response.status_code == 400
