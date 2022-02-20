from card import *
from datetime import datetime, timedelta
import pandas as pd
import random
from collections import deque


class Deck():
    def __init__(self):
        self.cards = pd.DataFrame(
            columns=["next review date", "term", "quality", "card"])
        # self.allCards = pd.DataFrame(columns= ['Card'])
        self.learn_today = deque([])  # deque of card objects
        self.size = 0
        # TODO add this
        self.progress = None  # % of cards that have 4 or higher quality score / total cards

    def get_todays_cards(self):
        todays_cards = self.cards[self.cards['next review date'].date() <=
                                  datetime.today().date()]['term'].tolist()
        return todays_cards

    def addCard(self, term, importance=1, tags=[]):
        card = Card(term, importance, tags)
        self.cards = self.cards.append(
            {
                "next review date": card.nextReviewDate,
                "term": term,
                "quality": card.quality,
                "card": card  # temporary until we set up a server/database
            },
            ignore_index=True)
        #
        #self.allCards = self.allCards.append({'Card': card}, ignore_index = True)
        self.learn_today.append(card)
        self.size += 1

    def deleteCard(self, card):
        self.cards.drop([card.nextReviewDate, card.english, card.quality])
        self.size -= 1

    # TODO add this
    def updateProgress(self):
        return 0

    def practice(self):
        self.learn_today = self.get_todays_cards().sample(frac=1)
        while (self.learn_today != None):
            self.learn_today.iloc(0)
            self.learn_today.iloc(0).drop
