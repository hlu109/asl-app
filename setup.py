from flask_sqlalchemy import SQLAlchemy
from flask import Flask
import os

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    if os.getenv(key='DATABASE_URL'):
        app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
            'DATABASE_URL').replace("postgres://", "postgresql://", 1)

    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    app.app_context().push()
    tear_down()  #TODO: need to remove later
    return app


def tear_down():
    db.session.remove()
    db.drop_all()
