from shared_db import db
from card import *
from datetime import datetime, timedelta
import pandas as pd
import random
from collections import deque


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
        self.learn_today = deque([])  # deque of card objects
        self.in_session = False

    def update_todays_cards(self):
        # TODO: UPDATE THIS
        todays_cards = self.cards.index[
            self.cards['next review date'] <= datetime.today().date()].tolist()
        # todays_cards = self.cards[self.cards['next review date'] <=
        #                           datetime.today().date()]['term'].tolist()
        random.shuffle(todays_cards)
        self.learn_today = deque(todays_cards)
        print(self.cards.head(6))

    def getCard(self, term):
        card = self.cards.at[term, "card"]
        return card

    def addCard(self, term, importance=1, tags=[]):
        card = Card(term, importance, tags)
        if term not in self.cards.index:
            self.cards.loc[term] = [card.nextReviewDate, card.quality, card]
        return card

    def deleteCard(self, term):
        self.cards.drop(term, inplace=True)

    # TODO add this
    def updateProgress(self, term, quality):
        print('updating deck')
        # TODO: verify that card is inside this deck
        assert term in self.cards.index
        card = self.cards.at[term, 'card']
        card.update_quality(quality)

        # update deck dataframe
        self.cards.at[term, "next review date"] = card.nextReviewDate
        self.cards.at[term, "quality"] = card.quality

        print(self.cards.head(6))

        # TODO: update today's deque if the card needs to be repeated
        if quality <= 1:
            self.learn_today.append(term)