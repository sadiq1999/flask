from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func


class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(10000))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class Active_user(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    age = db.Column(db.String(150))
    gender = db.Column(db.String(150))
    height = db.Column(db.String(150))
    weight = db.Column(db.String(150))
    goal_weight = db.Column(db.String(150))
    active1 = db.Column(db.String(150))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class food(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    days = db.Column(db.String(150))
    breakfast = db.Column(db.String(600))
    lunch = db.Column(db.String(600))
    dinner = db.Column(db.String(600))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    new_user = db.Column(db.String(150))  # 0 flase, 1 true
    notes = db.relationship('Note')
    active2 = db.relationship('Active_user')
    food2 = db.relationship('food')
