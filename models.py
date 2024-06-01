# pylint: disable= C0116,C0114,C0115
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    surname = db.Column(db.String(100), nullable=False)
    parent = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    address = db.Column(db.String(200), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    price_per_hour = db.Column(db.Integer, nullable=False)
    invoice_count = db.Column(db.Integer, default=1)

    def __repr__(self):
        return f'<Student {self.name} {self.surname}>'
