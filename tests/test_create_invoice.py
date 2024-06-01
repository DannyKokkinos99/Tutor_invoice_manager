import sys
sys.path.append('../')
from app import app


def test_get_create_invoice():
    with app.test_client() as c:
        response = c.get('/create-invoice-form')
        assert response.status_code == 200
        assert b'<h1 class="text-2xl font-bold mb-4 text-white">Generate Invoice</h1>' in response.data
        assert b'>Select Student</label>' in response.data
        assert b'Hours owed this week</label>' in response.data