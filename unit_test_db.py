from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql.functions import func
from flask_testing import TestCase
import unittest
import logging
import random

from card import Card, Media, History
from deck import Deck
from db import db

from webscrape import get_media
from datetime import datetime, date

logging.basicConfig(level=logging.DEBUG)

# let's just use terms with singular meanings for now
TEST_TERMS = [
    'apple',
    'name',
    'learn',
    'student',
    # 'teach',
    'teacher'
]


class MyTest(TestCase):

    def create_app(self):
        app = Flask(__name__)
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///unit_tests.db'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        # Dynamically bind SQLAlchemy to application
        db.init_app(app)
        app.app_context().push()  # apparently this does the binding?
        return app

    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    # helper function to populate database
    def populate_db(self, deck_name='test_deck', terms=TEST_TERMS):
        deck = Deck(name=deck_name)
        db.session.add(deck)
        db.session.commit()

        # card_dict = {}
        for term in terms:
            links = get_media(term)[0]
            logging.debug(links)
            card = deck.add_card(term, links)
            logging.debug(card.media[0].link)

    # test Deck constructor and querying
    def test_deck_constructor_query(self):
        """ only test constructing an empty deck
            (we will test adding stuff to decks later when we test other
            functions)
        """
        logging.info(
            "\n____________ TEST DECK CONSTRUCTOR TEST _________________ \n")
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
        logging.info(
            "\n____________ CARD CONSTRUCTOR TEST _________________ \n")
        deck = Deck(name='test_deck')
        db.session.add(deck)
        db.session.commit()

        card_list = []

        for term in TEST_TERMS:
            mp4s = get_media(term)[0]
            card = Card(
                english=term,
                mp4s=mp4s,
                deck_id=deck.id,
                # practice_id=deck.id,
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
        last_card_null_f = db.session.query(Card).filter(
            Card.id == last_id_null).first()
        last_card_null_a = db.session.query(Card).filter(
            Card.id == last_id_null).all()
        assert last_card_null_f == None
        assert last_card_null_a == []
        # print('last id query with no cards', last_id_null)
        card_dict = {}

        for term in TEST_TERMS:
            mp4s = get_media(term)[0]
            card = Card(
                english=term,
                mp4s=mp4s,
                deck_id=deck.id,
                # practice_id=deck.id
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
            db.and_(Card.deck.has(name=deck.name),
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
        card = Card(
            english=term,
            mp4s=mp4s,
            deck_id=deck.id,
            # practice_id=deck.id
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

        all_cards = Card.query.all()  # list of all cards that exist in the db
        logging.info('all_cards')
        logging.info(all_cards)

        # get a specific card
        apple_card = Card.query.filter(
            db.and_(Card.deck.has(name='test_deck'),
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
            db.and_(Card.deck.has(name='test_deck'),
                    Card.english == 'apple')).first()

        logging.info('apple_card.media')
        logging.info(apple_card.media)

        assert len(links) == len(apple_card.media)

        for media in apple_card.media:
            assert media.link in links

    # test different deletion queries
    def test_deletion_queries(self):
        logging.info("\n____________DELETION QUERIES TEST _________________ \n")

        self.populate_db()
        all_cards = Card.query.all()  # list of all cards that exist in the db
        logging.info('all_cards')
        logging.info(all_cards)

        # delete cards, testing 3 different queries
        db.session.query(Card).delete()
        db.session.commit()

        remaining_cards = db.session.query(Card).all()
        logging.info('remaining_cards after db.session.query(Card).delete()')
        logging.info(remaining_cards)

        # repeat with different delete query
        self.populate_db()
        all_cards = Card.query.all()  # list of all cards that exist in the db
        logging.info('all_cards')
        logging.info(all_cards)

        # delete cards via 2nd query
        Card.query.delete()
        db.session.commit()

        remaining_cards = db.session.query(Card).all()
        logging.info('remaining_cards after Card.query.delete()')
        logging.info(remaining_cards)

        # repeat with 3rd delete query
        logging.debug('now starting third deletion query')
        self.populate_db()
        logging.debug('database populated')
        all_cards = Card.query.all()  # list of all cards that exist in the db
        logging.info('all_cards')
        logging.info(all_cards)
        logging.info('media before deleting cards')
        logging.info(Media.query.all())

        # delete cards via 3rd query
        for card in all_cards:
            db.session.delete(card)
            db.session.commit()

        logging.info('third deletion completed')
        logging.info('media after deleting cards')
        logging.info(Media.query.all())

        remaining_cards = db.session.query(Card).all()
        logging.info(
            'remaining_cards after db.session.delete(card) with for loop')
        logging.info(remaining_cards)

        # TODO: i am just curious so I want to see what happens to deck when we delete all cards

    # test how to delete all cards and decks in database
    def test_delete_cards_first(self):
        logging.info(
            "\n____________DELETE CARDS FIRST TEST _________________ \n")
        self.populate_db()
        all_cards = Card.query.all()  # list of all cards that exist in the db
        logging.info('all_cards')
        logging.info(all_cards)

        # test deleting cards first, then deck, then media and history
        cards = db.session.query(Card).delete()
        db.session.commit()
        remaining_cards = db.session.query(Card).all()
        logging.info('remaining_cards')
        logging.info(remaining_cards)
        assert remaining_cards == []

        # decks = db.session.query(Deck).all()
        decks = db.session.query(Deck)
        logging.info('decks after cards are deleted')
        logging.info(decks.all())
        db.session.query(Deck).delete()
        db.session.commit()
        remaining_decks = db.session.query(Deck).all()
        logging.info('remaining decks after decks are deleted')
        logging.info(remaining_decks)
        assert remaining_decks == []  # Check if this is valid

        logging.info('media and history before deletion')
        logging.info(db.session.query(Media).all())
        logging.info(db.session.query(History).all())
        media = db.session.query(Media).delete()
        history = db.session.query(History).delete()
        db.session.commit()

        logging.info('media and history after deletion')
        logging.info(db.session.query(Media).all())
        logging.info(db.session.query(History).all())
        assert db.session.query(Media).all() == []
        assert db.session.query(History).all() == []

    def test_delete_decks_first(self):
        logging.info(
            "\n____________DELETE DECKS FIRST TEST _________________ \n")
        self.populate_db()
        all_cards = db.session.query(Card).all()
        logging.info('cards before')
        logging.info(all_cards)
        decks = db.session.query(Deck)
        logging.info('decks before deletion')
        logging.info(decks.all())
        db.session.query(Deck).delete()
        db.session.commit()
        remaining_decks = db.session.query(Deck).all()
        logging.info('decks after deletion')
        logging.info(remaining_decks)
        assert remaining_decks == []

        cards = db.session.query(Card)
        logging.info('cards before explicit deletion')
        logging.info(cards.all())
        db.session.query(Card).delete()
        db.session.commit()
        remaining_cards = db.session.query(Card).all()
        logging.info('cards after deletion')
        logging.info(remaining_cards)
        assert remaining_cards == []

        media = db.session.query(Media)
        history = db.session.query(History)
        logging.info('media and history before explicit deletion')
        logging.info(media.all())
        logging.info(history.all())
        db.session.query(Media).delete()
        db.session.query(History).delete()
        db.session.commit()
        remaining_media = db.session.query(Media).all()
        remaining_history = db.session.query(History).all()
        logging.info('media and history after deletion')
        logging.info(remaining_media)
        logging.info(remaining_history)
        assert remaining_media == [] and remaining_history == []

    # test getting cards to practice
    def test_get_practice_cards(self):
        logging.info(
            "\n____________GET PRACTICE CARDS TEST _________________ \n")
        pass
        # self.populate_db()
        # deck = Deck.query.filter_by(name='test_deck').first()
        # logging.info('deck\'s cards')
        # logging.info(deck.cards)
        # logging.info(deck.cards[0])

        # logging.info('deck\'s practice cards before adding any')
        # logging.info(deck.practice_cards)

        # # add cards to the practice table, in order
        # for card in deck.cards:
        #     card.add_to_practice()

        # logging.info('deck\'s practice cards after adding cards in order')
        # logging.info(deck.practice_cards)

        # # clear practice table
        # for card in deck.cards:
        #     card.remove_from_practice()

        # # add cards to the practice table, in random order
        # shuffled_deck = deck.cards
        # random.shuffle(shuffled_deck)
        # print(shuffled_deck)
        # for card in shuffled_deck:
        #     card.add_to_practice()

        # logging.info('deck\'s practice cards after adding cards randomly')
        # logging.info(deck.practice_cards)

    # test Card update quality
    def test_card_update_quality(self):
        pass

    def test_deck_size(self):
        logging.info("\n____________TEST DECK SIZE _________________ \n")

        # (a lot of duplicated code from populate_db() )
        deck = Deck(name='test deck')
        db.session.add(deck)
        db.session.commit()

        self.assertEquals(0, deck.size)
        for i, term in enumerate(TEST_TERMS):
            links = get_media(term)[0]
            logging.debug(links)
            card = deck.add_card(term, links)
            logging.debug(card.media[0].link)
            self.assertEquals(i + 1, deck.size)

        self.assertEquals(len(TEST_TERMS), deck.size)


if __name__ == "__main__":
    # run ```python3 unit_test_db.py &> unit_test.txt``` to pipe outputs to
    # text file
    unittest.main()