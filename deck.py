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
    progress = db.Column(db.Integer, default=0, nullable=False)
    # TODO: update this with % of cards that have 4 or higher quality score / total cards
    cards = db.relationship('Card', uselist=True, 
                            backref='deck', 
                            # back_populates='deck', 
                            # cascade='all, delete, delete-orphan',
                            passive_deletes=True)

    # check if we want to modify backref and lazy ?

    def __init__(self, **kwargs):
        super(Deck, self).__init__(**kwargs)
        # TODO: UPDATE HOW WE ITERATE OVER CARDS!!
        self.init_on_load()

    @orm.reconstructor
    def init_on_load(self):
        logging.debug('inside init on load')
        self.learn_today = deque([])  # deque of card objects
        self.in_session = False

    def update_todays_cards(self):
        todays_cards = Card.query.filter(
            db.and_(
                Card.deck.has(name=self.name),
                Card.next_review_date <= datetime.now())).all()
        logging.debug("todays_cards")
        for card in todays_cards:
            logging.debug(card.english)

        random.shuffle(todays_cards)
        self.learn_today = deque(todays_cards)

    def get_card(self, term):
        card = Card.query.filter(
            db.and_(Card.deck.has(name=self.name),
                    Card.english == term)).first()
            # db.and_(Card.deck.any(name=self.name),
            #         Card.english == term)).first()
            # db.and_(Card.deck.name == self.name,
            #         Card.english == term)).first()
            # # Card.deck is a comparator object (???)
        # card = self.cards.at[term, "card"]
        return card

    def add_card(self, term, mp4s, importance=1, tags=[]):
        if self.get_card(term) == None:
            card = Card(english=term,
                        mp4s=mp4s,
                        deck_id=self.id,
                        importance=importance,
                        # tags=tags
                        )
            logging.debug('term after card constructor')
            logging.debug(card.english)
            logging.debug('mp4s after card constructor')
            logging.debug(card.media)
            db.session.add(card)
            db.session.commit()
            return card
        else:
            # TODO: redirect to the view card page of term
            logging.warning('card already exists, pls update using a different function')
            return False

    def delete_card(self, term):
        self.get_card(term).delete()
        # TODO: do we need to check if the query = None?
        # self.cards.drop(term, inplace=True)
        db.session.commit()

    # TODO add this
    def update_progress(self, term, quality):
        logging.info('updating deck')
        # TODO: verify that card is inside this deck
        assert self.get_card(term) == None
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