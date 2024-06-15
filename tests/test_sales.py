import pytest

from flaskr.db import get_db

@pytest.mark.parametrize('path', (
    '/sales/',
    '/sales/1/products/'
))
def test_get(client, path):
    response = client.get(path)

    assert response.status_code == 200
    assert b'SaleID' in response.data

    assert client.get('/sales/3/products/').status_code == 404


def test_create(client, app):
    data = {
        #'UserID': '1',
    }

    assert client.post('/sales/', data=data).status_code == 200
    
    with app.app_context():
        assert get_db().execute(
            'SELECT * FROM Sale WHERE SaleID = 2'
        ).fetchone() is not None


def test_get_sale_total(client):
    response = client.get('/sales/1/total/')
    assert response.status_code == 200
    assert b'SaleTotal' in response.data
    assert b'7.9' in response.data

    assert client.get('/sales/3/total/').status_code == 404


def test_delete_sale(client, app):
    assert client.delete('/sales/1/').status_code == 200

    assert client.delete('/sales/3/').status_code == 404

    with app.app_context():
        assert get_db().execute(
            'SELECT * FROM Sale WHERE SaleID = 1',
        ).fetchone() is None

        assert get_db().execute(
            'SELECT * FROM SaleProduct WHERE SaleID = 1',
        ).fetchone() is None

        assert get_db().execute(
            'SELECT * FROM Product WHERE ProductID = 2'
        ).fetchone()['ProductStock'] == 70


def test_add_product(client, app):
    data = {
        'ProductID': '1',
        'Price': 0.99,
        'Amount': 5
    }

    assert client.post('/sales/1/products/', data=data).status_code == 200

    assert client.post('/sales/3/products/').status_code == 404

    with app.app_context():
        assert get_db().execute(
            'SELECT * FROM SaleProduct WHERE ProductID = 1',
        ).fetchone() is not None

        assert get_db().execute(
            'SELECT * FROM Sale WHERE SaleId = 1'
        ).fetchone()['SaleTotal'] == 7.9 + data['Amount'] * data['Price'] 

        assert get_db().execute(
            'SELECT * FROM Product WHERE ProductID = 1'
        ).fetchone()['ProductStock'] == 75


@pytest.mark.parametrize(('product_id', 'price', 'amount', 'message'), (
    ('', '', '', b'ProductID is required.'),
    ('a', '', '', b'ProductID need to be a integer.'),
    ('1', '', '', b'Price is required.'),
    ('1', 'a', '', b'Price need to be a number.'),
    ('1', '1', '', b'Amount is required.'),
    ('1', '1', 'a', b'Amount need to be a integer.'),
    ('2', '1', '1', b'Already exists.'),
))
def test_add_product_validade_input(client, product_id, price, amount, message):
    data={
        'ProductID': product_id,
        'Price': price,
        'Amount': amount
    }

    response = client.post('/sales/1/products/', data=data)
    assert message in response.data
    assert response.status_code == 400


def test_remove_product(client, app):
    assert client.delete('/sales/1/products/2/').status_code == 200

    assert client.delete('/sales/3/products/2/').status_code == 404
    assert client.delete('/sales/3/products/3/').status_code == 404

    with app.app_context():
        assert get_db().execute(
            'SELECT * FROM SaleProduct WHERE ProductID = 2',
        ).fetchone() is None

        assert get_db().execute(
            'SELECT * FROM Sale WHERE SaleId = 1'
        ).fetchone()['SaleTotal'] == 0

        response = get_db().execute(
            'SELECT * FROM Product WHERE ProductID = 2'
        ).fetchone()
        
        assert response['ProductStock'] == 70
