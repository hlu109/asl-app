from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql.functions import func
from flask_testing import TestCase
import unittest
import logging

from card import Card
from deck import Deck
from setup import db

from webscrape import get_media
from datetime import datetime, date

logging.basicConfig(level=logging.DEBUG)

# let's just use terms with singular meanings for now
TEST_TERMS = ['apple',
                'name',
                'learn',
                'student',
                'teach',
                'teacher']


class MyTest(TestCase):

    def create_app(self):
        logging.info("\n____________ CREATE APP TEST _________________ \n")
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
        """ only test constructing an empty deck 
            (we will test adding stuff to decks later when we test other 
            functions)
        """
        logging.info("\n____________ TEST DECK CONSTRUCTOR TEST _________________ \n")
        deck1 = Deck(name='test_deck1')
        deck2 = Deck(name='test_deck2')
        db.session.add(deck1)
        db.session.add(deck2)
        db.session.commit()

        decks = Deck.query.all()
        assert decks == [deck1, deck2]

        first_deck = Deck.query.filter_by(name='test_deck1').first()
        assert first_deck == deck1
        # yay, session does not get cleared after the first query
        
    def test_card_constructor(self):
        logging.info("\n____________ CARD CONSTRUCTOR TEST _________________ \n")
        deck = Deck(name='test_deck')
        db.session.add(deck)
        db.session.commit()

        card_list = []

        for term in TEST_TERMS:
            mp4s = get_media(term)[0]
            card = Card(english=term,
                        mp4s=mp4s,
                        deck_id=deck.id
                        )
            card_list += [card]
            db.session.add(card)
        
        db.session.commit()
        
        all_cards = Card.query.all()
        logging.debug('all_cards')
        logging.debug(all_cards)
        assert all_cards == card_list

    def test_card_query(self):
        # test querying for task id
        # compare when db is empty vs has cards 
        logging.info("\n____________ CARD QUERY TEST _________________ \n")
        deck = Deck(name='test_deck')
        db.session.add(deck)
        db.session.commit()
        
        # check what happens when we do a query on an empty db
        last_id_null = db.session.query(func.max(Card.id)).scalar()
        last_card_null_f= db.session.query(Card).filter(Card.id == last_id_null).first()
        last_card_null_a= db.session.query(Card).filter(Card.id == last_id_null).all()
        assert last_card_null_f == None
        assert last_card_null_a == []
        # print('last id query with no cards', last_id_null)
        card_dict = {}

        for term in TEST_TERMS:
            mp4s = get_media(term)[0]
            card = Card(english=term,
                        mp4s=mp4s,
                        deck_id=deck.id
                        )
            db.session.add(card)
            card_dict[term] = card
        
        db.session.commit()

        # verify that the id is as expected when the db is populated
        last_id = db.session.query(func.max(Card.id)).scalar()
        logging.info('last_id')
        logging.info(last_id)
        teacher_id = Card.query.filter(Card.english == 'teacher').first().id
        assert last_id == teacher_id

        # verify that the review date query is working
        deck.update_todays_cards()
        todays_cards = deck.learn_today

        todays_query = Card.query.filter(
            db.and_(
                Card.deck.has(name=deck.name),
                Card.next_review_date <= datetime.now())).all()

        print('todays_query')
        print(todays_query)
        
        logging.info('todays_cards')
        logging.info(todays_cards)
        logging.info('card dict values')
        logging.info(card_dict.values())
        assert len(todays_cards) == len(card_dict.values())
        for card in card_dict.values():
            assert card in todays_cards

    def test_get_card(self):
        logging.info("\n____________ GET CARD TEST _________________ \n")
        deck = Deck(name='test_deck')
        db.session.add(deck)
        db.session.commit()

        # verify what happens when card doesn't exist
        null_card = deck.get_card('apple')
        assert null_card == None
        
        # now add the card and verify that we can get it back
        term = 'apple'
        mp4s = get_media(term)[0]
        card = Card(english=term,
                    mp4s=mp4s,
                    deck_id=deck.id
                    )
        db.session.add(card)
        db.session.commit()

        apple_card = deck.get_card('apple')
        assert apple_card == card

    # test Card constructor and querying
    def test_add_card(self):
        logging.info("\n____________ ADD CARD TEST _________________ \n")
        deck = Deck(name='test_deck')
        db.session.add(deck)
        db.session.commit()
        
        card_dict = {}
        
        for term in TEST_TERMS:
            links = get_media(term)[0]
            logging.debug(links)
            card = deck.add_card(term, links)
            logging.debug(card.media[0].link)
            card_dict[term] = card
        
        all_cards = Card.query.all() # list of all cards that exist in the db
        logging.info('all_cards')
        logging.info(all_cards)
        
        # get a specific card
        apple_card = Card.query.filter(
                db.and_(
                    Card.deck.has(name='test_deck'),
                    Card.english == 'apple')).first()
        
        assert deck.get_card('apple') == apple_card
        assert card_dict['apple'] == apple_card
        

    # test media access
    def test_card_media(self):
        logging.info("\n____________ CARD MEDIA TEST _________________ \n")
        deck = Deck(name='test_deck')
        db.session.add(deck)
        db.session.commit()

        links = get_media('apple')[0]
        card = deck.add_card('apple', links)

        apple_card = Card.query.filter(
                db.and_(
                    Card.deck.has(name='test_deck'),
                    Card.english == 'apple')).first()
        
        logging.info('apple_card.media')
        logging.info(apple_card.media)
        
        assert len(links) == len(apple_card.media)

        for media in apple_card.media:
            assert media.link in links

    # test Card update quality
    def test_card_update_quality(self):
        pass




if __name__ == "__main__":
    unittest.main()