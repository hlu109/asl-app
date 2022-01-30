from deck import *
from card import *

test_deck = Deck()

terms = [
    'apple', 
    'happy', 
    'sign', 
    'name', 
    'person', 
    'learn', 
    'student', 
    'teach', 
    'teacher'
    ]

for term in terms:
    test_deck.addCard(term)