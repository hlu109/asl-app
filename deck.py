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
        self.in_session = False
        # TODO add this
        self.progress = None  # % of cards that have 4 or higher quality score / total cards

    def update_todays_cards(self):
        todays_cards = self.cards[self.cards['next review date'] <=
                                  datetime.today().date()]['term'].tolist()
        random.shuffle(todays_cards)
        self.learn_today = deque(todays_cards)

    def addCard(self, term, importance=1, tags=[]):
        card = Card(term, importance, tags)
        # TODO: check that card does not already exist in the dataframe
        # TODO: use term as index
        self.cards = self.cards.append(
            {
                "next review date": card.nextReviewDate,
                "term": term,
                "quality": card.quality,
                "card": card  # temporary until we set up a server/database
            },
            ignore_index=True)
        # self.learn_today.append(card)
        self.size += 1

    def deleteCard(self, card):
        self.cards.drop([card.nextReviewDate, card.english, card.quality])
        self.size -= 1

    # TODO add this
    def updateProgress(self, card, quality):
        print('updating deck')
        # TODO: verify that card is inside this deck
        card.updateQuality(quality)

        # update deck dataframe
        card_entry = self.cards.loc[self.cards[
            "term"] == card.english]  # card_entry is a row in the dataframe
        # print(card_entry)
        # print(type(card_entry))
        card_entry["next review date"] = card.nextReviewDate
        card_entry["quality"] = card.quality
        # print('next review date:', card.nextReviewDate)

        # TODO: update today's deque if the card needs to be repeated

    # def practice(self):
    #     self.learn_today = deque(self.update_todays_cards())
    # while (self.learn_today != None):
    #     self.learn_today.iloc(0)
    #     self.learn_today.iloc(0).drop
