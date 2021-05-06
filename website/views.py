from flask import Blueprint, render_template, request, flash, jsonify, redirect
from flask_login import login_required, current_user
from .models import Note, Active_user, food, User
from . import db
import json
import random
import os

views = Blueprint('views', __name__)


@views.route('/')  # url
def home():
    plan()
    return render_template("home.html", user=current_user)


@views.route('/YourPlan', methods=['GET', 'POST'])
@login_required
def YourPlan():
    BMI = 0
    BMI_Category = ''
    Cal_to_loss = 0
    goal_w = 0
    goal_time = 0
    Active_user1 = Active_user.query.filter_by(user_id=current_user.id).first()
    if Active_user1:
        # BMI calculater:
        BMI = float(Active_user1.weight) / (float(Active_user1.height) * float(Active_user1.height) * 0.0001)
        BMI = round(BMI, 1)
        # BMI for 20 years and older
        if int(Active_user1.age) > 20:
            if BMI <= 16:
                BMI_Category = 'Severe Thinness'
            elif BMI > 16 and BMI <= 17:
                BMI_Category = 'Moderate Thinness'
            elif BMI > 17 and BMI <= 18.5:
                BMI_Category = 'Mild Thinness'
            elif BMI > 18.5 and BMI <= 25:
                BMI_Category = 'Normal'
            elif BMI > 25 and BMI <= 30:
                BMI_Category = 'Overweight'
            elif BMI > 30 and BMI <= 35:
                BMI_Category = 'Obese Class I'
            elif BMI > 35 and BMI <= 40:
                BMI_Category = 'Obese Class II'
            elif BMI > 40:
                BMI_Category = 'Obese Class III'
        # BMI for less than 20 years
        else:
            if BMI <= 14.5:
                BMI_Category = 'Underweight'
            elif BMI > 14.5 and BMI <= 20.2:
                BMI_Category = 'Healthy weight'
            elif BMI > 20.2:
                BMI_Category = 'Overweight'
        # BMR calculater for Male & Female:
        BMR = 0
        if Active_user1.gender == 'Male':
            BMR = (10 * float(Active_user1.weight)) + (6.25 * float(Active_user1.height)) - (5 * int(Active_user1.age)) + 5
        else:
            BMR = (10 * float(Active_user1.weight)) + (6.25 * float(Active_user1.height)) - (5 * int(Active_user1.age)) - 161
        # Physical Activity Level (PAL):
        PAL = 0
        if Active_user1.active1 == 'Sedentary Active: little or no exercise':
            PAL = 1.2
        elif Active_user1.active1 == 'Lightly Active: 1-3 times/week':
            PAL = 1.375
        elif Active_user1.active1 == 'Moderately Active: 4-5 times/week':
            PAL = 1.55
        elif Active_user1.active1 == 'Very Active: 6-7 times/week':
            PAL = 1.725
        # Cal to loss 0.5 kg/week
        Cal_to_loss = int(BMR * PAL - 500)
        # Goal weight
        goal_w = float(Active_user1.goal_weight)
        goal_time = int((float(Active_user1.weight) - goal_w) / 0.5)
    return render_template(
        'YourPlan.html',
        user=current_user,
        BMI=BMI,
        BMI_Category=BMI_Category,
        Cal_to_loss=Cal_to_loss,
        goal_w=goal_w,
        goal_time=goal_time)


@views.route('/note', methods=['GET', 'POST'])
@login_required
def note():
    if request.method == 'POST':
        note = request.form.get('note')

        if len(note) < 1:
            flash('Note is empty!', category='error')
        else:
            new_note = Note(data=note, user_id=current_user.id)
            db.session.add(new_note)
            db.session.commit()
            flash('Note added!', category='success')
    return render_template('note.html', user=current_user)


@views.route('delete-note', methods=['POST'])
def delete_note():
    note = json.loads(request.data)
    noteId = note['noteId']
    note = Note.query.get(noteId)
    if note:
        if note.user_id == current_user.id:
            db.session.delete(note)
            db.session.commit()
    return jsonify({})


@views.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    user1 = db.session.query(User).get(current_user.id)
    if request.method == 'POST':
        age = request.form.get('age')
        gender = request.form.get('gender')
        height = request.form.get('height')
        weight = request.form.get('weight')
        goal_weight = request.form.get('goal-weight')
        active1 = request.form.get('active')

        if len(age) < 1 or len(height) < 1 or len(weight) < 1 or len(goal_weight) < 1:
            flash('There is/are some field empty!', category='error')
        else:
            new_settings = Active_user(
                age=age,
                gender=gender,
                height=height,
                weight=weight,
                goal_weight=goal_weight,
                active1=active1,
                user_id=current_user.id)
            db.session.add(new_settings)
            user1.new_user = '1'
            db.session.commit()
            flash('Settings saved!', category='success')
            plan()

    return render_template('settings.html', user=current_user)


@views.route('/changeSetting', methods=['GET', 'POST'])
@login_required
def change_settings():
    Active_user1 = Active_user.query.filter_by(user_id=current_user.id).first()
    if request.method == 'POST':
        age = request.form.get('age')
        gender = request.form.get('gender')
        height = request.form.get('height')
        weight = request.form.get('weight')
        goal_weight = request.form.get('goal-weight')
        active1 = request.form.get('active')

        if len(age) < 1 or len(height) < 1 or len(weight) < 1 or len(goal_weight) < 1:
            flash('There is/are some field empty!', category='error')

        else:
            Active_user1.age = age
            Active_user1.gender = gender
            Active_user1.height = height
            Active_user1.weight = weight
            Active_user1.goal_weight = goal_weight
            Active_user1.active1 = active1
            db.session.commit()
            plan()
            return redirect('/settings')
    return render_template('changeSetting.html', user=current_user)


@views.route('/plan', methods=['GET', 'POST'])
@login_required
def plan():

    if request.method == 'POST':
        num_month1 = 28  # For Ex
        Cal_to_loss = 1999
        breakfastCal = round(Cal_to_loss * (30 / 100))
        lunchCal = round(Cal_to_loss * (40 / 100))
        dinnerCal = round(Cal_to_loss * (30 / 100))

        # first make sure db is clear
        food.query.filter_by(user_id=current_user.id).delete()

        while num_month1 > 0:
            breakfast = random_json(breakfastCal, 'breakfast')
            lunch = random_json(lunchCal, 'lunch')
            dinner = random_json(dinnerCal, 'dinner')

            new_food = food(
                breakfast=breakfast,
                lunch=lunch,
                dinner=dinner,
                user_id=current_user.id
            )

            db.session.add(new_food)
            db.session.commit()
            num_month1 -= 1

    return render_template('plan.html', user=current_user)


@views.route('/exercises')
@login_required
def exercises():
    return render_template('exercises.html', user=current_user)


def random_json(maxCal, category):
    SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
    json_url = os.path.join(SITE_ROOT, "static", "food.json")
    with open(json_url) as d:
        data = json.load(d)

    cal = maxCal
    countCal = cal
    food_json = []
    food_list = []

    for food1 in data[category]:
        food_json.append(food1)

    random.shuffle(food_json)

    for food1 in food_json:
        if food1['cal'] <= countCal:
            food_list.append(food1['name'])
            countCal -= food1['cal']

    r = ','.join(food_list)
    return r


@views.route('/loading')
@login_required
def loading():
    return render_template('loading.html', user=current_user)
