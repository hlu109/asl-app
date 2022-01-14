from datetime import datetime, timedelta
from supermemo2 import SMTwo
from pandas import DataFrame as df


class HistoricalPerformance():
    def __init__(self):
        self.history = df(columns=["date", "quality"])

    def add_record(self, date, quality):
        self.history.append({"date": date, "quality": quality})

class Card():

    def __init__(self, term, importance=1, tags = []):
        self.english = term
        self.media = [] # list of links to mp4s, images, etc
        self.description = ""
        self.hint = ""
        # TODO: try to get hint/description from the text file
        self.importance = importance
        self.history = HistoricalPerformance()
        self.sm2Data = None # type SMTwo
        # self.SM2data will contain the easiness score, interval, and next 
        # review date
        # update self.sm2Data once the user is tested on this word to be 
        # SMTwo.first_review(quality, datetime.today())
        self.lastReviewDate = None
        # This has the format "datetime.datetime(2022, 1, 13, 16, 50, 31, 568809)"
        self.nextReviewDate = None
        self.tags = tags
    
    def getQuality(self):
        """ placeholder function for now """
        quality = None 
        return quality

    def reviewCard(self):
        quality = self.getQuality()
        self.lastReviewDate = datetime.today()
        if self.sm2Data == None:
            self.sm2Data = SMTwo.first_review(self.lastReviewDate, quality)
        else: 
            self.sm2Data.review(self.lastReviewDate, quality)
        interval = timedelta(days = self.sm2Data.interval) 
        # TODO: update algorithm to all for shorter intervals (e.g. 10 min)
        self.nextReviewDate = self.lastReviewDate + interval
    
    # create function to get Hint
    # create function to display card

    
    

