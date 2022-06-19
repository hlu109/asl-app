from shared_db import db
from datetime import datetime, timedelta
from supermemo2 import SMTwo
# import pandas as pd


class Media(db.Model):
    __tablename__ = 'media'
    id = db.Column(db.Integer, primary_key=True)
    link = db.Column(db.Text, nullable=False)
    card_id = db.Column(db.Integer, db.ForeignKey('card.id'), nullable=False)
    # might be useful when we have different media on different cards with the same term


class History(db.Model):
    __tablename__ = 'history'
    card_id = db.Column(db.Integer, db.ForeignKey('card.id'), primary_key=True)
    review_date = db.Column(db.DateTime, nullable=False)  # yyyy-mm-dd format
    quality = db.Column(db.Integer, nullable=False)


class Card(db.Model):
    __tablename__ = 'card'
    ## identifiers and user-facing card components ##
    id = db.Column(db.Integer, primary_key=True)
    english = db.Column(db.Text, nullable=False)
    media = db.relationship('Media', uselist=True, backref='card')
    deck_id = db.Column(db.Integer, db.ForeignKey('deck.id'), nullable=False)

    ## performance-related ##
    last_review_date = db.Column(db.DateTime, nullable=True)
    last_EF = db.Column(db.Integer, default=-1, nullable=False)
    last_interval = db.Column(db.Integer, default=-1, nullable=False)
    repetitions = db.Column(db.Integer, default=0, nullable=False)
    next_review_date = db.Column(db.DateTime,
                                 default=datetime.now,
                                 nullable=False)
    quality = db.Column(db.Integer, default=0, nullable=False)
    history = db.relationship('History', uselist=True, backref='card')

    ## other helpful attributes ##
    description = db.Column(db.Text, nullable=True)
    hint = db.Column(db.Text, nullable=True)
    importance = db.Column(db.Integer, nullable=True)

    def __init__(self, english, mp4s, deck_id, **kwargs):
        # user only needs to pass in english, media, link it to a deck somehow ?
        # and can optionally pass in description, hint, and importance
        for link in mp4s:
            db.session.add(Media(link=link, card_id=self.id))
        db.session.commit()
        # self.media = list of Media objs? 

        super(Card, self).__init__(english, deck_id, **kwargs)

        
        # self.deck_id = ??
        # TODO: how do we add a deck id ???

        # TODO: create subclass? to account for different directions of review
        # (i.e. ASLtoEng or EngtoASL)
        # self.english = term
        # self.media = []  # list of links to media
        # self.description = ""
        # self.hint = ""  #Need to find hint in ASL Browser notes text file
        # # TODO: try to get hint/description from the text file
        # self.importance = importance
        # self.sm2Data = None  # obj of type SMTwo
        # self.SM2data will contain the easiness score, interval, and next
        # review date
        # update self.sm2Data once the user is tested on this word to be
        # SMTwo.first_review(quality, datetime.today())
        # self.lastReviewDate = None # type string
        # self.last_EF = None # type int
        # self.last_interval = None # type int
        # self.repetitions = 0 # type int
        # # This has the format "datetime.datetime(2022, 1, 13, 16, 50, 31, 568809)"
        # self.nextReviewDate = datetime.today().date().strftime('%Y-%m-%d') #type string
        # self.tags = tags : can add later if we want
        # self.qualEngtoASL = 0
        # self.qualASLtoEng = 0
        # self.quality = 0
        # self.history = [] # list of tuples (review date, quali)

    def update_quality(self, quality):
        self.quality = quality

        if self.last_review_date == None:  # new card
            sm2 = SMTwo.first_review(self.quality, datetime.today().date())
        else:
            sm2 = SMTwo(self.last_EF, self.last_interval, self.repetitions)
            sm2.review(self.quality, datetime.today().date())

        self.last_review_date = datetime.today().date()
        self.last_EF = sm2.easiness
        self.repetitions = sm2.repetitions
        self.last_interval = sm2.interval

        interval = timedelta(days=sm2.interval)
        # TODO: update algorithm for shorter intervals (e.g. 10 min)
        self.nextReviewDate = (self.last_review_date + interval)

        review_instance = History(review_date=self.last_review_date,
                                  quality=self.quality,
                                  card_id=self.id)
        db.session.add(review_instance)
        db.session.commit()

    # TODO: create function to get Hint
    def get_hint(self):
        """ placeholder, when user clicks 'Get Hint' button, hint appears
            we update the hint variable from the ASL Browser notes text file
        """
        #Create dictionary from the ASL Browser notes which stores the mp4 file and hint text
        hint = ''
        self.hint = hint
        db.session.commit()
