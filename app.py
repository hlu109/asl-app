from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from deck import *
from card import *
from webscrape import *
from testing import test_deck

app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
# db = SQLAlchemy(app)

# TEMPORARY LIST OF ALL DECKS (SO WE CAN TEST THE APP WITHOUT A DB)
ALL_DECKS = {"Test Deck": test_deck}

# class DeckDB(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(200), nullable=False)


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/decks', methods=['POST', 'GET'])
def view_all_decks():
    if request.method == 'POST':
        print('HANDLING POST REQUEST TO CREATE NEW DECK')
        new_deck_name = request.form['new_deck_name']
        # deck_index = len(ALL_DECKS) + 1
        new_deck = Deck()
        ALL_DECKS[new_deck_name] = new_deck

    return render_template("decks.html", decks=ALL_DECKS)


@app.route('/<string:deck_name>')
def view_deck(deck_name):
    deck = ALL_DECKS[deck_name]
    return render_template("viewDeck.html", deck=deck, deck_name=deck_name)


@app.route('/<string:deck_name>/practice', methods=['POST', 'GET'])
# inputs: deck, queue of cards to learn today, mode: ASL or English first (add this later)
# need button to reveal back of card
# then need button for quality
# then add checkbox to review again - bool
# return post, quality, bool for review again
def practice(deck_name):
    deck = ALL_DECKS[deck_name]
    if not deck.in_session:
        deck.update_todays_cards()
        deck.in_session = True

    if not deck.learn_today:  # if empty
        deck.in_session = False
        return "no more flashcards to practice today"
        # TODO: route back to page that tells them they are done practicing
        #on that page, add button to go back to deck

    print("\n\n\n\n\n", deck.learn_today, "\n\n\n\n\n")

    # front = True
    # TODO: add code to deal with displaying english vs displaying ASL
    # (english front asl back)

    if request.method == 'POST':
        print('HANDLING POST REQUEST')
        quality_term = request.form['quality-term']
        quality = int(quality_term.split("-")[0])
        term = quality_term.split("-")[1]

        deck.updateProgress(term, quality)
        return redirect('/' + deck_name + '/practice')
    else:
        next_card_term = deck.learn_today.popleft()
        next_card = getCard(deck_name, next_card_term)
        return render_template("practice.html",
                               deck_name=deck_name,
                               card=next_card)


@app.route('/<string:deck_name>/<string:card_term>', methods=['POST', 'GET'])
def view_card(deck_name, card_term):
    if request.method == 'POST':
        print('HANDLING POST REQUEST TO ADD MEDIA')
        mp4_keep = request.form['myData'].split(",")

        # update the card's media
        card = getCard(deck_name, card_term)
        links = get_media(card_term)[0]
        for i in range(len(mp4_keep)):
            if mp4_keep[i] == '1':
                card.media += [links[i]]
    else:
        card = getCard(deck_name, card_term)
    return render_template("viewCard.html", card=card)


@app.route('/<string:deck_name>/select_term', methods = ['POST'])
def select_term(deck_name):
    print('HANDLING POST REQUEST TO CREATE NEW CARD')
    new_term = request.form['new_term']
    results = get_terms(new_term)
    
    if results == None: # no search results
        return render_template("wordNotFound.html")
    elif len(results) == 1: 
        # if the word has a unique result, redirect to select_media
        # return redirect('/' + deck_name + '/select_media/' + new_term, 
        #                 # data= , "search/" + new_term 
        #                 code=307) 
        return redirect(url_for("select_media", deck_name = deck_name, 
               new_term = new_term, url_suffix = "search/" + new_term))
        # TODO: Figure out data passing in redirect, use urlfor()
    else:
        return render_template("selectTerm.html", deck_name=deck_name, 
                        results=results)
# TODO!!! check all instances of get_media and ensure that they are using 
# url_suffix if necessary, currently videos are not showing up for run

# TODO: perhaps make the new_term parameter hidden from the url somehow?
@app.route('/<string:deck_name>/select_media/<string:new_term>', 
           methods=['POST'])
def select_media(deck_name, new_term):
    print('HANDLING POST REQUEST TO CREATE NEW CARD')
    # new_term  = request.form["new_term"]
    url_suffix  = request.form["url_suffix"]
    print(url_suffix)
    new_card = ALL_DECKS[deck_name].addCard(new_term)
    mp4s = get_media(new_term, url_suffix)

    return render_template("selectMedia.html", card=new_card, 
                        deck_name=deck_name, mp4s=mp4s)


####### helper functions #######
def getCard(deck_name, card_term):
    deck = ALL_DECKS[deck_name]
    # card_entries = deck.cards[deck.cards['term'] == card_term]
    print(deck.cards)
    if card_term in deck.cards.index:
        card = deck.cards.at[card_term, 'card']
    else:
        raise Exception("The card " + card_term + " doesn't exist")
    # elif len(card_entries) > 1:
    #     raise Exception("There are multiple cards with the term " + card_term)

    # card = card_entries.card.values[0]
    return card


if __name__ == "__main__":
    app.run(debug=True)
