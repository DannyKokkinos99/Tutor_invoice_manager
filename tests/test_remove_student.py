import sys
sys.path.append('../')
from app import app


def test_remove_student():
    with app.test_client() as c:
        response = c.get('/remove-student')
        assert response.status_code == 200
        assert b'<h1 class="text-2xl font-bold mb-4 text-white">Remove Student</h1>' in response.data
        assert b'Select Student to be removed</label>' in response.data
        assert b'Cancel' in response.data
        assert b'Remove' in response.data
