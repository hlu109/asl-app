from shared_db import db
from card import Card
from datetime import datetime, timedelta
# import pandas as pd
import random
from collections import deque
from sqlalchemy import orm


class Deck(db.Model):
    __tablename__ = 'deck'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    progress = db.Column(db.Integer, default=0, nullable=False)
    # TODO: update this with % of cards that have 4 or higher quality score / total cards
    cards = db.relationship('Card', uselist=True, backref='deck')

    # check if we want to modify backref and lazy ?

    def __init__(self, **kwargs):
        super(Deck, self).__init__(**kwargs)
        # TODO: UPDATE HOW WE ITERATE OVER CARDS!!
        self.init_on_load()

    @orm.reconstructor
    def init_on_load(self):
        print('init on load')
        self.learn_today = deque([])  # deque of card objects
        self.in_session = False

    def update_todays_cards(self):
        # TODO: UPDATE THIS
        todays_cards = Card.query.filter(
            db.and_(
                Card.deck.h(name=self.name).all(),
                Card.next_review_date <= datetime.today().date()))
        print("todays_cards \n", todays_cards)
        # self.cards['next review date'] <= datetime.today().date()].tolist()
        # todays_cards = self.cards[self.cards['next review date'] <=
        #                           datetime.today().date()]['term'].tolist()
        random.shuffle(todays_cards)
        self.learn_today = deque(todays_cards)
        # print(self.cards.head(6))

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
        # TODO: check if card is already in deck
        if self.get_card(term) == None:
            card = Card(english=term,
                        mp4s=mp4s,
                        deck_id=self.id,
                        importance=importance,
                        # tags=tags
                        )
            db.session.add(card)
            db.session.commit()
            return card
        else:
            print('card already exists, pls update using a different function')
            return False

    def delete_card(self, term):
        self.get_card(term).delete()
        # TODO: do we need to check if the query = None?
        # self.cards.drop(term, inplace=True)
        db.session.commit()

    # TODO add this
    def update_progress(self, term, quality):
        print('updating deck')
        # TODO: verify that card is inside this deck
        assert self.get_card(term) == None
        # assert term in self.cards.index
        card = self.get_card(term)
        card.update_quality(quality)

        # # update deck dataframe
        # self.cards.at[term, "next review date"] = card.nextReviewDate
        # self.cards.at[term, "quality"] = card.quality

        # print(self.cards.head(6))

        # TODO: update today's deque if the card needs to be repeated
        if quality <= 1:
            self.learn_today.append(card)