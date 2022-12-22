from flask_sqlalchemy import SQLAlchemy
import sqlalchemy
from flask import Flask
import os
import logging
from logging.handlers import RotatingFileHandler
from flask.logging import default_handler
# from deck import Deck
# from card import Card
# import webscrape

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

    # Check if the database needs to be initialized
    engine = sqlalchemy.create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
    inspector = sqlalchemy.inspect(engine)
    if True:
        # if not inspector.has_table("card") and not inspector.has_table("deck"):
        with app.app_context():
            tear_down()
            # db.drop_all()
            db.create_all()

            # # add a test deck to the db
            # make_test_deck()

            app.logger.info('Initialized the database!')
    else:
        app.logger.info('Database already contains the cards and decks tables.')

    return app

    # tear_down()  #TODO: need to remove later
    return app


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
