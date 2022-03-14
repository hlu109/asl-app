import pandas as pd

data = {'next review date': [], 'term': [], 'quality': []}
cards = pd.DataFrame(data)
cards = cards.set_index('term')  # drop default true

# cards = pd.DataFrame(columns=["next review date", "term", "quality", "card"])
print(cards)
# cards.set_index('term', inplace=True)
# cards = cards.set_index('term')

cards.loc['term1'] = ['date', 1]
cards.loc['e'] = ['date', 1]
# cards = cards.append(
#     {
#         "next review date": 1,
#         # "term": "a",
#         "quality": 0,
#         "card": "ignore"  # temporary until we set up a server/database
#     },
#     # ignore_index=True
#     index=["a"])
# # cards.set_index('term', inplace=True)
# cards = cards.set_index('term')

# cards = cards.append(
#     {
#         "next review date": 1,
#         # "term": "b",
#         "quality": 1,
#         "card": "ignore"  # temporary until we set up a server/database
#     },
#     # ignore_index=True
#     index=["b"])
# cards = cards.append(
#     {
#         "next review date": 1,
#         # "term": "c",
#         "quality": 2,
#         "card": "ignore"  # temporary until we set up a server/database
#     },
#     # ignore_index=True
#     index=["c"])
# cards = cards.append(
#     {
#         "next review date": 1,
#         # "term": "d",
#         "quality": 3,
#         "card": "ignore"  # temporary until we set up a server/database
#     },
#     index=["d"])
# cards = cards.append(
#     {
#         "next review date": 1,
#         # "term": "e",
#         "quality": 4,
#         "card": "ignore"  # temporary until we set up a server/database
#     },
#     index=["e"])

print(cards.head())
print(cards.loc["e", 'quality'])
print(cards.at["e", 'quality'])
print("e" in cards.index)
cards.drop('e', inplace=True)
print(cards.head())
