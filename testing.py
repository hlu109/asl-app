from webbrowser import get
from deck import *
from card import *

test_deck = Deck()

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
    test_deck.addCard(term)
    card = test_deck.getCard(term)
    card.media = get_media(term)[0]
