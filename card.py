from setup import db
from datetime import datetime, timedelta
from supermemo2 import SMTwo

from sqlalchemy.sql.functions import func
# import pandas as pd

import logging

logging.basicConfig(level=logging.INFO)


class Media(db.Model):
    __tablename__ = 'media'
    id = db.Column(db.Integer, primary_key=True)
    link = db.Column(db.Text, nullable=False)
    card_id = db.Column(db.Integer,
                        db.ForeignKey('card.id', ondelete='CASCADE'),
                        nullable=False)
    # card = db.relationship('Card', back_populates='media')


class History(db.Model):
    __tablename__ = 'history'
    id = db.Column(db.Integer, primary_key=True)
    card_id = db.Column(db.Integer, db.ForeignKey('card.id',
                                                  ondelete='CASCADE'))
    review_date = db.Column(db.DateTime, nullable=False)  # yyyy-mm-dd format
    quality = db.Column(db.Integer, nullable=False)
    # card = db.relationship('Card', back_populates='history')


class Card(db.Model):
    __tablename__ = 'card'
    ## identifiers and user-facing card components ##
    id = db.Column(db.Integer, primary_key=True)
    english = db.Column(db.Text, nullable=False)
    media = db.relationship(
        'Media',
        uselist=True,  # indicates should be loaded as list 
        # (not scalar)
        backref='card',
        # back_populates='card',
        # cascade = 'all, delete, delete-orphan',
        passive_deletes=True)
    deck_id = db.Column(db.Integer,
                        db.ForeignKey('deck.id', ondelete='CASCADE'),
                        nullable=False)
    # practice_id = db.Column(db.Integer,
    #                         db.ForeignKey('deck.id', ondelete='CASCADE'),
    #                         nullable=True)
    # deck = db.relationship('Deck', back_populates='cards')

    ## performance-related ##
    last_review_date = db.Column(db.DateTime, nullable=True)
    last_EF = db.Column(db.Integer, default=-1, nullable=False)
    last_interval = db.Column(db.Integer, default=-1, nullable=False)
    repetitions = db.Column(db.Integer, default=0, nullable=False)
    next_review_date = db.Column(db.DateTime,
                                 default=datetime.now,
                                 nullable=False)
    quality = db.Column(db.Integer, default=0, nullable=False)
    review_again = db.Column(db.Boolean, default=False)
    history = db.relationship(
        'History',
        uselist=True,
        #   cascade = 'all, delete, delete-orphan',
        #   backref = 'card',
        #   back_populates = 'card',
        passive_deletes=True)

    ## other helpful attributes ##
    description = db.Column(db.Text, nullable=True)
    hint = db.Column(db.Text, nullable=True)
    importance = db.Column(db.Integer, nullable=True)

    def __init__(self, english, mp4s, deck_id, **kwargs):
        # user only needs to pass in english, media, link it to a deck somehow ?
        # and can optionally pass in description, hint, and importance
        # self.media = sqlalchemy.orm.collections.InstrumentedList object
        kwargs['english'] = english
        kwargs['deck_id'] = deck_id

        card_id = self.generate_id()
        self.id = card_id

        super(Card, self).__init__(**kwargs)
        # todo: add something to check if the super() is updating self.id
        # right now when we are testing, self.id and card_id are the same so
        # we don't know if super() is overriding anything (with the same value)
        logging.debug('self.id', self.id)
        logging.debug('card_id', card_id)
        # print('inside card constructor, now printing links:')
        for link in mp4s:
            # TODO: add error handling to ensure mp4s is not empty
            # print(link)
            db.session.add(Media(link=link, card_id=card_id))
        db.session.commit()

        # self.deck_id = ??
        # TODO: how do we add a deck id ???

    def generate_id(self):
        """ stupid simple id generator that returns autoincrementing integers 
            for card ids to get around inability to access self.id inside the 
            __init__() method
        """
        db_size = db.session.query(func.count(Card.id)).scalar()

        if db_size == 0:
            return 1
        else:
            # if the db contains any cards, we have to find the current highest
            # id separately because its possible that max_id != # cards (e.g.
            # if we deleted any cards)
            max_id = db.session.query(func.max(Card.id)).scalar()
            return max_id + 1

    # def add_to_practice(self):
    #     """ add the card to its deck's practice table """
    #     self.practice_id = self.deck_id
    #     db.session.commit()

    # def remove_from_practice(self):
    #     """ remove the card from its deck's practice table """
    #     self.practice_id = None
    #     db.session.commit()

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
        self.next_review_date = (self.last_review_date + interval)

        if quality <= 2:
            self.review_again = True
        else:
            self.review_again = False

        review_instance = History(review_date=self.last_review_date,
                                  quality=self.quality,
                                  card_id=self.id)
        db.session.add(review_instance)
        db.session.commit()
        logging.info('self.next_review_date: ' + str(self.next_review_date))
        logging.info('self.review_again: ' + str(self.review_again))

    # TODO: create function to get Hint
    def get_hint(self):
        """ placeholder, when user clicks 'Get Hint' button, hint appears
            we update the hint variable from the ASL Browser notes text file
        """
        #Create dictionary from the ASL Browser notes which stores the mp4 file and hint text
        hint = ''
        self.hint = hint
        db.session.commit()

    def delete(card):
        # delete all associated media and history objects first

        # now delete the card itself

        # TODO: add a custom function for mass deletion (e.g. clearing an entire db)
        pass
