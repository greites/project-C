import pytest

def test_index(client, app):
    data = {
        'ProductID': '1',
        'Price': 0.99,
        'Amount': 60
    }

    assert client.post('/sales/1/products/', data=data).status_code == 200

    with app.app_context():
        response = client.get('/notes/')

        assert response.status_code == 200
        assert b'NoteID' in response.data