from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_testing import TestCase
import unittest

from card import Card
from deck import Deck
from shared_db import db

from webscrape import get_media
from datetime import datetime

# let's just use terms with singular meanings for now
TEST_TERMS = ['apple',
                'name',
                'learn',
                'student',
                'teach',
                'teacher']



class MyTest(TestCase):

    def create_app(self):
        app = Flask(__name__)
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///unit_tests.db'
        # Dynamically bind SQLAlchemy to application
        db.init_app(app)
        app.app_context().push() # apparently this does the binding?
        return app

    def setUp(self):
        db.create_all()
    
    def tearDown(self):
        db.session.remove()
        db.drop_all()


    # test Deck constructor and querying
    def test_deck_constructor_query(self):
        # only test constructing an empty deck
        # (we will test adding stuff to decks later when we test other functions)
        deck1 = Deck(name='test_deck1')
        deck2 = Deck(name='test_deck2')
        db.session.add(deck1)
        db.session.add(deck2)
        db.session.commit()

        decks = Deck.query.all()
        # TODO: check if session is cleared after query
        
        assert decks == [deck1, deck2]
        first_deck = Deck.query.filter_by(name='test_deck1').first()

        assert first_deck == deck1
        


    # test Card constructor and querying
    def test_card_constructor_query(self):
        deck = Deck(name='test_deck')
        db.session.add(deck)
        db.session.commit()
        
        card_dict = {}
        
        # TODO: FIX THE QUERY IN DECK.GET_CARD()
        for term in TEST_TERMS:
            links = get_media(term)[0]
            card = deck.add_card(term, links)
            card_dict[term] = card
        
        all_cards = Card.query.all() # list of all cards that exist in the db
        print(all_cards)
        
        # get a specific card
        apple_card = Card.query.filter(
                db.and_(
                    Card.deck.any(name='test_deck'),
                    Card.english == 'apple')).first()
        
        assert deck.get_card('apple') == apple_card
        assert card_dict['apple'] == apple_card
        
        # get a list of cards filtered by review date
        todays_cards = Card.query.filter(
                db.and_(
                    Card.deck.any(name='test_deck'),
                    Card.next_review_date <= datetime.today().date())).all()
        
        assert todays_cards == card_dict.values()

    # test Card update quality
    def test_card_update_quality(self):
        pass

    # test Deck init on load

    # test Deck querying

    # test Deck update_todays_cards

    # test Deck get_card

    # test Deck add_card

    # test Deck delete_card



if __name__ == "__main__":
    unittest.main()