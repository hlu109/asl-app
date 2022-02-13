from datetime import datetime, timedelta
from supermemo2 import SMTwo
import pandas as pd

from webscrape import get_media


class HistoricalPerformance():
    def __init__(self):
        self.history = pd.DataFrame(columns=["date", "quality"])

    def add_record(self, date, quality):
        self.history.append({
            "date": date,
            "quality": quality
        },
                            ignore_index=True)


class Card():
    def __init__(self, term, importance=1, tags=[]):
        # TODO: create subclass? to account for different directions of review
        # (i.e. ASLtoEng or EngtoASL)
        self.english = term
        self.media = self.getMedia()  # list of links to mp4s, images, etc
        self.description = ""
        self.hint = ""  #Need to find hint in ASL Browser notes text file
        # TODO: try to get hint/description from the text file
        self.importance = importance
        self.history = HistoricalPerformance()
        self.sm2Data = None  # obj of type SMTwo
        # self.SM2data will contain the easiness score, interval, and next
        # review date
        # update self.sm2Data once the user is tested on this word to be
        # SMTwo.first_review(quality, datetime.today())
        self.lastReviewDate = None
        # This has the format "datetime.datetime(2022, 1, 13, 16, 50, 31, 568809)"
        self.nextReviewDate = datetime.today()
        self.tags = tags
        # self.qualEngtoASL = 0
        # self.qualASLtoEng = 0
        self.quality = 0

    def getMedia(self):
        print("attempting to get media for ", self.english)
        mp4s, labels = get_media(self.english)
        media = {"mp4s": mp4s, "labels": labels}
        # placeholder
        return media

    def getQuality(self):
        """ placeholder function for now. get the quality that the user selects
            when the term is tested 
        """
        quality = None
        self.quality = quality
        # if form == "EngtoASL": self.qualEngtoASL = quality
        # elif form == "ASLtoEng": self.qualASLtoEng = quality
        return quality

    def reviewCard(self):
        self.getQuality()
        self.lastReviewDate = datetime.today()
        if self.sm2Data == None:
            self.sm2Data = SMTwo.first_review(self.lastReviewDate, self.quality)
        else:
            self.sm2Data.review(self.lastReviewDate, self.quality)
        interval = timedelta(days=self.sm2Data.interval)
        # TODO: update algorithm for shorter intervals (e.g. 10 min)
        self.nextReviewDate = self.lastReviewDate + interval

    # create function to get Hint
    def getHint(self):
        """placeholder, when user clicks 'Get Hint' button, hint appears
            we update the hint variable from the ASL Browser notes text file
        """
        #Create dictionary from the ASL Browser notes which stores the mp4 file and hint text
        return self.hint
