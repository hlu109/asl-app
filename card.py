from shared_db import db
from datetime import datetime, timedelta
from supermemo2 import SMTwo
from sqlalchemy.sql.functions import func
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
        # self.media = list? of Media objs? 
        print('kwargs')
        print(kwargs)

        kwargs['english'] = english
        kwargs['deck_id'] = deck_id
        print('kwargs after')
        print(kwargs)

        card_id = self.generate_id()
        self.id = card_id
        
        super(Card, self).__init__(**kwargs)
        # todo: add something to check if the super() is updating self.id
        # right now when we are testing, self.id and card_id are the same so
        # we don't know if super() is overriding anything (with the same value)
        print('self.id', self.id)
        print('card_id', card_id)

        for link in mp4s:
            db.session.add(Media(link=link, card_id=card_id))
        db.session.commit()
        
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

    def generate_id(self):
        """ stupid simple id generator that returns autoincrementing integers 
            for card ids to get around inability to access self.id inside 
            __init__()
        """
        db_size = db.session.query(func.count(Card.id)).scalar()
        # last_id = db.session.query(Card).order_by(Card.id.desc()).first().id()
        # print('last_id 1', last_id)
        # print('last_id 2', last_id)

        if db_size == 0:
            return 1
        else: 
            last_card = db.session.query(Card).filter(Card.id == func.max(Card.id)).first()
            print('last id type', type(last_card))
            print('last_card.id()', last_card.id()) 
            # print('last_card.id', last_card.id) 
            last_id = last_card.id()
            return last_id + 1

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
