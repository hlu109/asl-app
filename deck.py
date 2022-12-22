from setup import db
from card import Card

from datetime import datetime, timedelta
import random
from collections import deque
# import pandas as pd

from sqlalchemy import orm
import logging

logging.basicConfig(level=logging.INFO)


class Deck(db.Model):
    __tablename__ = 'deck'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    in_session = db.Column(db.Boolean, default=False)
    progress = db.Column(db.Integer, default=0, nullable=False)
    # TODO: update this with % of cards that have 4 or higher quality score / total cards
    cards = db.relationship(
        'Card',
        foreign_keys='Card.deck_id',
        uselist=True,
        backref='deck',
        # back_populates='deck',
        # cascade='all, delete, delete-orphan',
        passive_deletes=True)

    # TODO: ensure that cards we've seen at least once today are added to the end of the practice queue, so that we make sure to practice all cards before repeating failed cards. perhaps use a separate relationship (e.g. practice_cards) to somehow track the order of cards?
    # practice_cards = db.relationship(
    #     'Card',
    #     foreign_keys='Card.practice_id',
    #     uselist=True,
    #     # backref='deck',
    #     # back_populates='deck',
    #     # cascade='all, delete, delete-orphan',
    #     passive_deletes=True)

    # check if we want to modify backref and lazy ?

    def __init__(self, **kwargs):
        super(Deck, self).__init__(**kwargs)
        # TODO: UPDATE HOW WE ITERATE OVER CARDS!!
        self.init_on_load()

    @orm.reconstructor
    def init_on_load(self):
        logging.debug('inside init on load')
        self.learn_today = deque([])  # deque of card objects
        # self.in_session = False

    def update_todays_cards(self):
        todays_cards = Card.query.filter(
            db.and_(Card.deck.has(name=self.name),
                    Card.next_review_date <= datetime.now())).all()
        logging.debug("todays_cards")
        for card in todays_cards:
            logging.debug(card.english)

        random.shuffle(todays_cards)
        # add cards to the practice_cards column
        for card in todays_cards:
            pass
            # how ?????

        self.learn_today = deque(todays_cards)

    def get_card(self, term):
        logging.info('all cards:')
        logging.info(Card.query.all())
        card = Card.query.filter(
            db.and_(
                Card.deck_id == self.id,
                # Card.deck.has(name=self.name),
                Card.english == term)).first()
        # db.and_(Card.deck.any(name=self.name),
        #         Card.english == term)).first()
        # db.and_(Card.deck.name == self.name,
        #         Card.english == term)).first()
        # # Card.deck is a comparator object (???)
        # card = self.cards.at[term, "card"]
        return card

    def add_card(self, term, mp4s, importance=1, tags=[]):
        logging.info('does card already exist? self.get_card(term)')
        logging.info(self.get_card(term))
        if self.get_card(term) == None:
            card = Card(
                english=term,
                # mp4s=mp4s,
                mp4s=None,
                deck_id=self.id,
                # practice_id=self.id,
                importance=importance,
                # tags=tags
            )
            db.session.add(card)
            card.add_media(mp4s)
            db.session.commit()

            logging.debug('term after card constructor')
            logging.debug(card.english)
            logging.debug('mp4s after card constructor')
            logging.debug(card.media)
            return card
        else:
            # TODO: redirect to the view card page of term
            logging.warning(
                'card already exists, pls update using a different function')
            return False

    def delete_card(self, term):
        self.get_card(term).delete()
        # TODO: do we need to check if the query = None?
        # self.cards.drop(term, inplace=True)
        db.session.commit()

    def get_practice_card(self):
        todays_cards = Card.query.filter(
            db.and_(
                Card.deck.has(name=self.name),
                db.or_(Card.next_review_date <= datetime.now(),
                       Card.review_again == True))).all()
        logging.debug("todays_cards")
        print("todays_cards")
        for card in todays_cards:
            logging.debug(card.english)
            print(card.english, card.next_review_date, card.review_again)

        if not todays_cards:  # query is empty
            return None
        return random.choice(todays_cards)

    def update_progress(self, term, quality):
        logging.info('updating deck')
        # TODO: verify that card is inside this deck
        assert self.get_card(term) != None
        # assert term in self.cards.index
        card = self.get_card(term)
        card.update_quality(quality)

        # # update deck dataframe
        # self.cards.at[term, "next review date"] = card.nextReviewDate
        # self.cards.at[term, "quality"] = card.quality

        # TODO: update today's deque if the card needs to be repeated
        if quality <= 1:
            self.learn_today.append(card)

    def delete(self):
        pass