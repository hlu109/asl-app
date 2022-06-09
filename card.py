from shared_db import db
from datetime import datetime, timedelta
from supermemo2 import SMTwo
import pandas as pd


class Card(db.Model):
    def __init__(self, term, importance=1, tags=[]):
        # TODO: create subclass? to account for different directions of review
        # (i.e. ASLtoEng or EngtoASL)
        self.english = term
        self.media = []  # list of links to media
        self.description = ""
        self.hint = ""  #Need to find hint in ASL Browser notes text file
        # TODO: try to get hint/description from the text file
        self.importance = importance
        # self.sm2Data = None  # obj of type SMTwo
        # self.SM2data will contain the easiness score, interval, and next
        # review date
        # update self.sm2Data once the user is tested on this word to be
        # SMTwo.first_review(quality, datetime.today())
        self.lastReviewDate = None # type int
        self.last_EF = None # type int
        self.last_interval = None # type int
        self.repetitions = 0 # type int
        # This has the format "datetime.datetime(2022, 1, 13, 16, 50, 31, 568809)"
        self.nextReviewDate = datetime.today().date()
        self.tags = tags
        # self.qualEngtoASL = 0
        # self.qualASLtoEng = 0
        self.quality = 0
        self.history = [] # list of tuples (review date, quali)


    def updateQuality(self, quality):
        self.quality = quality

        if self.lastReviewDate == None: # new card
            sm2 = SMTwo.first_review(self.quality, datetime.today().date())
        else:
            sm2 = SMTwo(self.last_EF, self.last_interval, self.repetitions)
            sm2.review(self.quality, datetime.today().date())
        
        self.lastReviewDate = datetime.today().date()
        self.last_EF = sm2.easiness
        self.repetitions = sm2.repetitions
        self.last_interval = sm2.interval
            
        interval = timedelta(days=sm2.interval)
        # TODO: update algorithm for shorter intervals (e.g. 10 min)
        self.nextReviewDate = self.lastReviewDate + interval
        self.history.append((self.lastReviewDate, self.quality))

    # TODO: create function to get Hint
    def getHint(self):
        """ placeholder, when user clicks 'Get Hint' button, hint appears
            we update the hint variable from the ASL Browser notes text file
        """
        #Create dictionary from the ASL Browser notes which stores the mp4 file and hint text
        return self.hint
