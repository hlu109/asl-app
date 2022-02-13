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

print(type(test_deck.cards[test_deck.cards['term']=='learn'].card.values[0]))
# print(test_deck.cards[test_deck.cards['term']=='learn'].loc[:, "card"].head())