from setup import db, create_app

from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from deck import Deck
from card import Card
import webscrape
from testing import make_test_deck

import logging

logging.basicConfig(level=logging.INFO)

app = create_app()
db.create_all(app=app)

# add a test deck to the db
# make_test_deck()


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/decks', methods=['POST', 'GET'])
def view_all_decks():
    if request.method == 'POST':
        logging.info('HANDLING POST REQUEST TO CREATE NEW DECK')
        new_deck_name = request.form['new_deck_name']
        new_deck = Deck(name=new_deck_name)
        db.session.add(new_deck)
        db.session.commit()
    
    all_decks = db.session.query(Deck).all()
    return render_template("decks.html", decks=all_decks)


@app.route('/<string:deck_name>')
def view_deck(deck_name):
    cards = db.session.query(Card).filter(
        Card.deck.has(name=deck_name)).all()
    # TODO: add error handling
    return render_template("viewDeck.html", deck_name=deck_name, cards=cards)


@app.route('/<string:deck_name>/practice', methods=['POST', 'GET'])
# inputs: deck, queue of cards to learn today, mode: ASL or English first (add this later)
# need button to reveal back of card
# then need button for quality
# then add checkbox to review again - bool
# return post, quality, bool for review again
def practice(deck_name):
    deck = db.session.query(Deck).filter_by(name = deck_name).first()
    # TODO: add error handling
    if not deck.in_session:
        deck.update_todays_cards()
        deck.in_session = True

    logging.debug("\n\n\n\n\n", deck.learn_today, "\n\n\n\n\n")

    # front = True
    # TODO: add code to deal with displaying english vs displaying ASL
    # (english front asl back)

    if request.method == 'POST':
        logging.info('HANDLING POST REQUEST')
        quality_term = request.form['quality-term']
        quality = int(quality_term.split("-")[0])
        term = quality_term.split("-")[1]

        deck.update_progress(term, quality)
        return redirect('/' + deck_name + '/practice')

    if not deck.learn_today:  # if empty
        deck.in_session = False
        return "no more flashcards to practice today"
        # TODO: route back to page that tells them they are done practicing
        #on that page, add button to go back to deck

    else:  # first starting the practice session
        next_card_term = deck.learn_today.popleft()
        next_card = get_card(deck_name, next_card_term)
        return render_template("practice.html",
                               deck_name=deck_name,
                               card=next_card)


@app.route('/<string:deck_name>/<string:card_term>', methods=['POST', 'GET'])
def view_card(deck_name, card_term):
    if request.method == 'POST':
        logging.info('HANDLING POST REQUEST TO ADD MEDIA')
        if request.form['new_card'] == 'True':
            mp4_keep = request.form['mp4_keep'].split(",")
            url_suffix = request.form['url_suffix']
            mp4s = idx_to_links(card_term, url_suffix, mp4_keep)
            deck = db.session.query(Deck).filter_by(name = deck_name).first()
            # TODO: add error handling
            card = deck.add_card(card_term, mp4s)
        else: # in this case we'd be editing/updating an existing card
            pass 
            # card = update_card(deck_name, card_term, mp4_keep, url_suffix)
    else:
        card = get_card(deck_name, card_term)
    return render_template("viewCard.html", card=card)


@app.route('/<string:deck_name>/select_term', methods=['POST'])
def select_term(deck_name):
    logging.info('HANDLING POST REQUEST TO CREATE NEW CARD')
    new_term = request.form['new_term']
    results = webscrape.get_terms(new_term)

    if results == None:  # no search results
        return render_template("wordNotFound.html")
    elif len(results) == 1:
        # if the word has a unique result, redirect to select_media
        return render_template("redirectToSelectMedia.html",
                               deck_name=deck_name,
                               term=new_term)
    else:
        return render_template("selectTerm.html",
                               deck_name=deck_name,
                               results=results)


# TODO!!! check all instances of get_media and ensure that they are using
# url_suffix if necessary, currently videos are not showing up for run


# TODO: perhaps make the new_term parameter hidden from the url somehow?
# TODO: the mp4 links are incorrect repeats https://signingsavvy... 
@app.route('/<string:deck_name>/select_media/<string:new_term>',
           methods=['POST'])
def select_media(deck_name, new_term):
    logging.info('HANDLING POST REQUEST TO CREATE NEW CARD')
    # new_term  = request.form["new_term"]
    url_suffix = request.form["url_suffix"]
    logging.debug(url_suffix)
    # new_card = ALL_DECKS[deck_name].add_card(new_term)
    mp4s = webscrape.get_media(new_term, url_suffix)

    return render_template("selectMedia.html",
                           term=new_term,
                           deck_name=deck_name,
                           mp4s=mp4s,
                           url_suffix=url_suffix)


####### helper functions #######
def get_card(deck_name, card_term):
    cards = Card.query.filter(
            db.and_(Card.deck.has(name=deck_name),
                    Card.english == card_term)).all()
    if cards == None:
        raise Exception("The card " + card_term + " doesn't exist")
        # TODO: maybe redirect to add card page?
    elif len(cards) > 1:
        raise Exception(f"There are multiple cards with the term {card_term} in deck {deck_name}")
    return cards[0]


#TODO: add description
def update_card(deck_name, card_term, mp4_keep, url_suffix=None):
    card = get_card(deck_name, card_term)
    # TODO: update this function
    card.media = idx_to_links(card_term, url_suffix, mp4_keep)
    # links = get_media(card_term, url_suffix)[0]
    # for i in range(len(mp4_keep)):
    #     if mp4_keep[i] == '1':
    #         card.media += [links[i]]
    return card

def idx_to_links(card_term, url_suffix, mp4_keep):
    links = webscrape.get_media(card_term, url_suffix)[0]
    mp4s = []
    for i in range(len(mp4_keep)):
        if mp4_keep[i] == '1':
            mp4s += [links[i]]
    return mp4s

if __name__ == "__main__":
    app.run(debug=True)
