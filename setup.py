from flask_sqlalchemy import SQLAlchemy
from flask import Flask

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
    db.init_app(app)
    app.app_context().push()
    tear_down() #TODO: need to remove later
    return app

def tear_down():
    db.session.remove()
    db.drop_all()
