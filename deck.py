from card import *
from datetime import datetime, timedelta
import pandas as pd

class Deck():

    def __init__(self):
        self.cards = pd.DataFrame(columns=["next review date", "term", "quality"]) 
        self.learn_today = [] # list of card objects
        self.size = 0
        # TODO add this 
        self.progress = None # % of cards that have 4 or higher quality score / total cards 

        
    def get_todays_cards(self):
        todays_cards = self.cards[self.cards['next review date'] == datetime.today()]['term'].tolist()
        return todays_cards
    
    def addCard(self, term, importance=1, tags = []):
        card = Card(term, importance, tags)
        self.cards.append(
            {
                "next review date" : card.nextReviewDate, 
                "term" : term, 
                "quality": card.quality
            }, 
            ignore_index=True)
        self.learn_today.append(card)
        self.size += 1
    
    def deleteCard(self, card):
        self.cards.drop([card.nextReviewDate, card.english, card.quality])
        self.size -= 1
    
    # TODO add this 
    def updateProgress(self):
        return 0

    def practice(self):
        self.learn_today = self.get_todays_cards()
        pass
