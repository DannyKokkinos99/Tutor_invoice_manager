import sys
sys.path.append('../')
from app import app


def test_home_route():
    with app.test_client() as c:
        response = c.get('/')
        assert response.status_code == 200
        assert b'<title>Tutoring Portal</title>' in response.data
        assert b'Create Invoice' in response.data
        assert b'Add Student' in response.data
        assert b'Edit Student' in response.data
        assert b'Remove Student' in response.data