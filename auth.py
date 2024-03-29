from flask import Flask, render_template, request, redirect, url_for, Blueprint, flash
from flask_login import login_user, login_required, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from user import User
from db import db

# create blueprints 
auth = Blueprint('auth', __name__)

# define routing for auth
@auth.route('/login', methods=['POST'])
def login():
    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False

    user = User.query.filter_by(email=email).first()

    # check if the user actually exists
    # take the user-supplied password, hash it, and compare it to the hashed password in the database
    if not user: # if the user doesn't exist, reload the page
        flash('Invalid email', category="login")
        return redirect(url_for('main.index')) 
    if not check_password_hash(user.password, password): # password is wrong, reload the page
        flash('Incorrect password', category="login")
        return redirect(url_for('main.index')) 

    # if the above check passes, then we know the user has the right credentials
    login_user(user, remember=remember)
    return redirect(url_for('main.view_all_decks'))

@auth.route('/signup', methods=['POST'])
def signup():
    # code to validate and add user to database goes here
    email = request.form.get('email')
    password = request.form.get('password')

    if email == "":
        flash('Email can\'t be empty', category="signup")
        return redirect(url_for('main.index'))
    # should we allow empty passwords? 
    # if password == "":
    #     flash('Password can\'t be empty', category="signup")
    #     return redirect(url_for('main.index'))

    user = User.query.filter_by(email=email).first() # if this returns a user, then the email already exists in database

    if user: # if a user is found, we want to redirect back to signup page so user can try again
        flash('Email already used', category="signup")
        return redirect(url_for('main.index'))

    # create a new user with the form data. Hash the password so the plaintext version isn't saved.
    new_user = User(email=email, password=generate_password_hash(password, method='sha256'))

    # add the new user to the database
    db.session.add(new_user)
    db.session.commit()

    # autoamtically log the user in this time 
    login_user(new_user)
    return redirect(url_for('main.view_all_decks'))

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))
