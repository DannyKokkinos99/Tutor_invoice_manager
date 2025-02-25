# pylint: disable= C0116,C0114,C0115
import secrets
import os
from flask import Flask
from dotenv import load_dotenv
from config import SQLALCHEMY_DATABASE_URI, SQLALCHEMY_TRACK_MODIFICATIONS
from gdrive import Gdrive
from emailer import Emailer
from extensions import db
from routes import app_routes


GOOGLE_DOC = "1pnp-XjBkuIb0LnspKW3d2uw2v6l7Byxxfuwgy5b0Oak"
PARENT_FOLDER_ID = "1--qhpO7fr5q4q7x0pRxdiETcFyBsNOGN"  # FOUND IN URL
TAX_RETURNS_FOLDER_ID = "1bpqM7ZChtiegKoJvV1MLpwIZ2PuKSLtv"
SERVICE_ACCOUNT_FILE = (
    "service_account.json"  # GIVE FOLDER PERMISSIONS TO SERVICE ACCOUNT
)
SCOPE = [
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/drive.readonly",
]  # do not change this
LOCAL_PARENT_FOLDER = "Invoices"
TAX_PARENT_FOLDER = "Invoices"

load_dotenv()


def create_app():
    app_local = Flask(__name__)
    app_local.config["SECRET_KEY"] = secrets.token_hex(16)
    app_local.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
    app_local.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = SQLALCHEMY_TRACK_MODIFICATIONS
    db.init_app(app_local)
    # Register the routes blueprint
    app_local.register_blueprint(app_routes)
    # Create all database tables
    with app_local.app_context():
        db.create_all()
    return app_local


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
