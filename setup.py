from flask_sqlalchemy import SQLAlchemy
import sqlalchemy
from flask import Flask
import os
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


# def make_test_deck():
#     deck = Deck(name='test_deck')
#     db.session.add(deck)
#     db.session.commit()

#     terms = [
#         'apple',
#         # 'happy', # lol webscraping is not working for some reason on this term
#         # 'sign', # webscrape doesn't work when there are multiple links for a term
#         'name',
#         # 'person',
#         'learn',
#         'student',
#         # 'teach', # has multiple results
#         'teacher'
#     ]

#     for term in terms:
#         media, labels = webscrape.get_media(term)
#         deck.add_card(term, media)
#         # card = deck.get_card(term, media)
