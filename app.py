import secrets
import os
from flask import Flask
from dotenv import load_dotenv
from config import SQLALCHEMY_DATABASE_URI, SQLALCHEMY_TRACK_MODIFICATIONS
from emailer import Emailer
from extensions import db
from models import *
from routes import app_routes

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
