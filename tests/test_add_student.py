import sys
import os
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(ROOT_DIR)
sys.path.append(PROJECT_ROOT)
from app import app


def test_add_student():
    with app.test_client() as c:
        response = c.get('/add-student')
        assert response.status_code == 200
        assert b'<h1 class="text-2xl font-bold mb-4 text-white">Add Student</h1>' in response.data
        assert b'Name' in response.data
        assert b'Surname' in response.data
        assert b'Parent' in response.data
        assert b'Email' in response.data
        assert b'Address' in response.data
        assert b'Phone Number' in response.data
        assert b'Price per Hour' in response.data
        assert b'Cancel' in response.data
        assert b'Add' in response.data