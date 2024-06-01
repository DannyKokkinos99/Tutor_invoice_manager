# pylint: disable= C0116,C0114,C0115
import os

basedir = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'students.db')
SQLALCHEMY_TRACK_MODIFICATIONS = False
