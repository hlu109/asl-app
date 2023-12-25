from flask_login import UserMixin
from db import db

class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))

    decks = db.relationship(
        'Deck',
        foreign_keys='Deck.user_id',
        uselist=True,
        backref='user')
