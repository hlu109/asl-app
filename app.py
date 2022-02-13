from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from deck import *
from card import *
from testing import test_deck

app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
# db = SQLAlchemy(app)

# TEMPORARY LIST OF ALL DECKS (SO WE CAN TEST THE APP WITHOUT A DB)
all_decks = {"Test Deck": test_deck}

# class DeckDB(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(200), nullable=False)


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/decks')
def view_all_decks():
    return render_template("decks.html", decks=all_decks)


@app.route('/<string:deck_name>')
def view_deck(deck_name):
    deck = all_decks[deck_name]
    return render_template("viewDeck.html", deck=deck, deck_name=deck_name)


@app.route('/<string:deck_name>/practice')
def practice(deck_name):
    deck = all_decks[deck_name]
    cards_to_practice = deck.learn_today  # list of cards
    return "placeholder"


@app.route('/<string:deck_name>/<string:card_term>')
def view_card(deck_name, card_term):
    card = getCard(deck_name, card_term)
    return render_template("viewCard.html", card=card)


@app.route('/<string:deck_name>/<string:card_term>/viewHint')
def viewHint(deck_name, card_term):
    card = getCard(deck_name, card_term)
    pass


####### helper functions #######
def getCard(deck_name, card_term):
    deck = all_decks[deck_name]
    card_entries = deck.cards[deck.cards['term'] == card_term]

    if card_entries.empty:
        raise Exception("The card " + card_term + " doesn't exist")
    elif len(card_entries) > 1:
        raise Exception("There are multiple cards with the term " + card_term)

    card = card_entries.card.values[0]
    return card


if __name__ == "__main__":
    app.run(debug=True)
