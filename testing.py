from deck import Deck
from card import Card
import webscrape

from setup import db


def make_test_deck():
    deck = Deck(name='test_deck')
    db.session.add(deck)
    db.session.commit()

    terms = [
        'apple',
        # 'happy', # lol webscraping is not working for some reason on this term
        # 'sign', # webscrape doesn't work when there are multiple links for a term
        'name',
        # 'person',
        'learn',
        'student',
        'teach',
        'teacher'
    ]

    for term in terms:
        media, labels = webscrape.get_media(term)
        deck.add_card(term, media)
        # card = deck.get_card(term, media)
