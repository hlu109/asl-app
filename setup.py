import sqlalchemy
from flask import Flask
import os
import logging
from logging.handlers import RotatingFileHandler
from flask.logging import default_handler
from flask_login import LoginManager

from .auth import auth as auth_blueprint
from .main import main as main_blueprint
from .db import db
from .user import User

def create_app():
    app = Flask(__name__)
    if os.getenv(key='DATABASE_URL'):
        app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
            'DATABASE_URL').replace("postgres://", "postgresql://", 1)

    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'secret-key-goes-here' # placeholder otherwise flask yells at us 
    db.init_app(app)

    # set up login manager
    login_manager = LoginManager()
    login_manager.login_view = "main.index" # redirect page if non-logged-in user tried to access a login-protected page 
    login_manager.init_app(app)

    # specify user loader
    @login_manager.user_loader
    def load_user(user_id):
        # since the user_id is just the primary key of our user table, use it in the query for the user
        return User.query.get(int(user_id))


    # register blueprints for authorization and non-auth pages 
    app.register_blueprint(auth_blueprint)
    app.register_blueprint(main_blueprint)

    app.app_context().push()

    # Check if the database needs to be initialized
    engine = sqlalchemy.create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
    inspector = sqlalchemy.inspect(engine)

    re_create_database = False # only for debugging 
    teardown = False # only for debugging  

    if re_create_database:
        with app.app_context():
            if teardown:
                tear_down()
            db.create_all()
            app.logger.info('re create_all database')
            
    elif not inspector.has_table("card") or not inspector.has_table("deck") or not inspector.has_table("user"):
        with app.app_context():
            tear_down()
            # db.drop_all()
            db.create_all()

            # # add a test deck to the db
            # make_test_deck()

            app.logger.info('Initialized the database!')
    else:
        app.logger.info('Database already contains the tables for users, decks, and cards.')

    return app

    # tear_down()  #TODO: need to remove later
    # return app


def tear_down():
    db.session.remove()
    db.drop_all()


def configure_logging(app):
    # Logging Configuration
    if app.config['LOG_WITH_GUNICORN']:
        gunicorn_error_logger = logging.getLogger('gunicorn.error')
        app.logger.handlers.extend(gunicorn_error_logger.handlers)
        app.logger.setLevel(logging.DEBUG)
    else:
        file_handler = RotatingFileHandler('instance/flask-user-management.log',
                                           maxBytes=16384,
                                           backupCount=20)
        file_formatter = logging.Formatter(
            '%(asctime)s %(levelname)s %(threadName)s-%(thread)d: %(message)s [in %(filename)s:%(lineno)d]'
        )
        file_handler.setFormatter(file_formatter)
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

    # Remove the default logger configured by Flask
    app.logger.removeHandler(default_handler)

    app.logger.info('Starting the Flask User Management App...')

