from db import db
from flask import Flask, render_template, request, redirect, url_for, Blueprint, flash
from flask_login import login_required, current_user
from deck import Deck
from card import Card
import webscrape
import logging
import pdb 

# create blueprints 
main = Blueprint('main', __name__)

# define routing for main
@main.route('/')
def index():
    return render_template("index.html")

@main.route('/decks', methods=['POST', 'GET'])
@login_required
def view_all_decks():
    if request.method == 'POST':
        logging.info('HANDLING POST REQUEST TO CREATE NEW DECK')
        new_deck_name = request.form['new_deck_name']
        new_deck = Deck(name=new_deck_name, user_id=current_user.id)
        db.session.add(new_deck)
        db.session.commit()
        return redirect(url_for('main.view_deck', deck_name=new_deck_name))

    all_decks = Deck.query.filter_by(user_id=current_user.id).all()
    return render_template("decks.html", decks=all_decks, email=current_user.email)


@main.route('/decks/<string:deck_name>', methods=["POST", "GET"])
@login_required
def view_deck(deck_name):
    logging.info("are we here?")
    if request.method == 'POST':
        logging.info('HANDLING POST REQUEST TO ADD MEDIA')
        if request.form['new_card'] == 'True':
            card_term = request.form['card_term']
            mp4_keep = request.form['mp4_keep'].split(",")
            logging.info(mp4_keep)
            url_suffix = request.form['url_suffix']
            logging.info(url_suffix)
            mp4s = idx_to_links(card_term, url_suffix, mp4_keep)
            logging.info(mp4s)
            deck = get_deck(deck_name, user_id=current_user.id)
            logging.info(deck)
            # TODO: add error handling
            card = deck.add_card(card_term, mp4s)
            logging.info(card)
        else:  # in this case we'd be editing/updating an existing card
            logging.info('inside else statement (should not get here)')
            pass
            # card = update_card(deck_name, card_term, mp4_keep, url_suffix)

    # retrieve all cards in the deck and display it
    cards = get_all_cards_in_deck(deck_name, user_id=current_user.id)

    # TODO: add error handling
    return render_template("viewDeck.html", deck_name=deck_name, cards=cards, email=current_user.email)


@main.route('/decks/<string:deck_name>/practice', methods=['POST', 'GET'])
# TODO add checkbox to review again - bool
# return post, quality, bool for review again
@login_required            
def practice(deck_name):
    deck = get_deck(deck_name, user_id=current_user.id)

    # TODO: add error handling
    if not deck.in_session:
        print('starting session')
        deck.in_session = True
        db.session.commit()

    # front = True
    # TODO: add code to deal with displaying english vs displaying ASL
    # (english front asl back)

    if request.method == 'POST':
        logging.info('HANDLING POST REQUEST')
        quality_term = request.form['quality-term']
        quality = int(quality_term.split("-")[0])
        term = quality_term.split("-")[1]
        deck.update_progress(term, quality)

        return redirect('/decks/' + deck_name + '/practice')

    else:
        next_card = deck.get_practice_card()

        if next_card is None:
            deck.in_session = False
            db.session.commit()
            return render_template("donePractice.html", deck_name=deck_name, email=current_user.email)

        else:  # first starting the practice session
            # next_card = deck.learn_today.popleft()
            # print('after queue pops left')
            # print(deck.learn_today)
            return render_template("practice.html",
                                   deck_name=deck_name,
                                   card=next_card, email=current_user.email)


@main.route('/decks/<string:deck_name>/<string:card_term>')
@login_required
def view_card(deck_name, card_term):
    card = get_card(deck_name, card_term, user_id=current_user.id)
    return render_template("viewCard.html", card=card, deck_name=deck_name, email=current_user.email)


@main.route('/decks/<string:deck_name>/select_term', methods=['POST'])
@login_required
def select_term(deck_name):
    logging.info('HANDLING POST REQUEST TO CREATE NEW CARD')
    new_term = request.form['new_term']
    results = webscrape.get_terms(new_term)

    if results == None:  # no search results
        flash("Word not found")
        return redirect(url_for('main.view_deck', deck_name=deck_name))
    elif len(results) == 1:
        # if the word has a unique result, redirect to select_media
        return render_template("redirectToSelectMedia.html",
                               deck_name=deck_name,
                               term=new_term, email=current_user.email)
    else: # multiple results
        return render_template("selectTerm.html",
                               deck_name=deck_name,
                               results=results, email=current_user.email)


# TODO: perhaps make the new_term parameter hidden from the url somehow?
@main.route('/decks/<string:deck_name>/select_media/<string:new_term>',
           methods=['POST'])
@login_required
def select_media(deck_name, new_term):
    logging.info('HANDLING POST REQUEST TO CREATE NEW CARD')
    # new_term  = request.form["new_term"]
    url_suffix = request.form["url_suffix"]
    logging.info(url_suffix)
    # new_card = ALL_DECKS[deck_name].add_card(new_term)
    mp4s = webscrape.get_media(new_term, url_suffix)

    return render_template("selectMedia.html",
                           term=new_term,
                           deck_name=deck_name,
                           mp4s=mp4s,
                           url_suffix=url_suffix, email=current_user.email)


####### helper functions #######
def get_deck(deck_name, user_id):
    deck = db.session.query(Deck).filter(
        db.and_(Deck.user_id==user_id,
                Deck.name==deck_name)).first()
    return deck

def get_all_cards_in_deck(deck_name, user_id):
    deck = get_deck(deck_name, user_id)
    cards = db.session.query(Card).filter(Card.deck == deck).all()
    return cards
    
def get_card(deck_name, card_term, user_id):
    deck = get_deck(deck_name, user_id)
    cards = db.session.query(Card).filter(
        db.and_(Card.deck == deck, Card.english == card_term)).all()
    if cards == None:
        raise Exception("The card " + card_term + " doesn't exist")
        # TODO: maybe redirect to add card page?
    elif len(cards) > 1:
        raise Exception(
            f"There are multiple cards with the term {card_term} in deck {deck_name}"
        )
    return cards[0]


#TODO: add description
def update_card(deck_name, card_term, mp4_keep, url_suffix=None):
    card = get_card(deck_name, card_term, user_id=current_user.id)
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

