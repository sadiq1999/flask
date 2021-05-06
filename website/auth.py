from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user

auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        Password = request.form.get('Password')

        # check in db for email and if find it stop (first)
        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, Password):
                flash('Log in successfully!', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('The email and/or password you entered are incorrect. Please try again', category='error')
        else:
            flash('The email and/or password you entered are incorrect. Please try again', category='error')
    #  data = request.form #data =  the input in login page
    return render_template("login.html", user=current_user)


@auth.route('/logout')
@login_required  # make sure cannot acssec this page unless user are login
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        firstName = request.form.get('firstName')
        Password1 = request.form.get('Password1')
        Password2 = request.form.get('Password2')

        user = User.query.filter_by(email=email).first()
        if user:
            flash('email already exisit. Please try again', category='error')
        elif len(email) < 4:
            flash('The email you entered is incorrect. Please try again', category='error')
        elif len(firstName) < 2:
            flash('firstName is too short. Please try again', category='error')
        elif Password1 != Password2:
            flash('password dont match. Please try again', category='error')
        elif len(Password1) < 7:
            flash('password is too short. Please try again', category='error')
        else:
            # add user to database
            new_user = User(
                email=email,
                first_name=firstName,
                password=generate_password_hash(Password1, method='sha256'),
                new_user='0')
            db.session.add(new_user)  # add user to db
            db.session.commit()  # update db
            login_user(new_user, remember=True)
            flash('Your account has been created successfully!', category='success')
            return redirect(url_for('views.home'))

    return render_template("sign_up.html", user=current_user)
