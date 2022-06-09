from shared_db import db
from card import *
from datetime import datetime, timedelta
import pandas as pd
import random
from collections import deque


class Deck(db.Model):
    def __init__(self):
        self.cards = pd.DataFrame(
            columns=["next review date", "term", "quality", "card"])
        self.cards.set_index('term', inplace=True)
        # self.allCards = pd.DataFrame(columns= ['Card'])
        self.learn_today = deque([])  # deque of card objects
        self.size = 0
        self.in_session = False
        # TODO add this
        self.progress = None  # % of cards that have 4 or higher quality score / total cards

    def update_todays_cards(self):
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
        self.size += 1
        return card

    def deleteCard(self, term):
        self.cards.drop(term, inplace=True)
        self.size -= 1

    # TODO add this
    def updateProgress(self, term, quality):
        print('updating deck')
        # TODO: verify that card is inside this deck
        assert term in self.cards.index
        card = self.cards.at[term, 'card']
        card.updateQuality(quality)

        # update deck dataframe
        self.cards.at[term, "next review date"] = card.nextReviewDate
        self.cards.at[term, "quality"] = card.quality

        print(self.cards.head(6))

        # TODO: update today's deque if the card needs to be repeated
        if quality <= 1:
            self.learn_today.append(term)