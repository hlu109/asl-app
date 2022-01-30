from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from deck import *
from card import *
from testing import test_deck

app = Flask(__name__)

# TEMPORARY LIST OF ALL DECKS (SO WE CAN TEST THE APP WITHOUT A DB)
all_decks = {"Test Deck" : test_deck}


@app.route('/')
def index():
    return "placeholder"

@app.route('/decks')
def view_all_decks():
    return render_template("decks.html", decks=all_decks)

@app.route('/<string:deck_name>')
def view_deck(deck_name):
    deck = all_decks[deck_name]
    return render_template("viewDeck.html", deck=deck)

@app.route('/<string:deck_name>/practice')
def practice(deck_name):
    deck = all_decks[deck_name]
    cards_to_practice = deck.learn_today # list of cards
    return "placeholder"


if __name__ == "__main__":
    app.run(debug=True)