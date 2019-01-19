import datetime
from functools import partial
from app import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timezone = db.Column(db.Integer, default=3)  #default for Moscow
    points = db.Column(db.Integer, default=0)
    bot_activated = db.Column(db.Boolean, default=True)
    role = db.Column(db.Integer, default=0)  # 0 - user, 1-admin

    partner_id = db.Column(db.Integer, db.ForeignKey('partner.id'))
    partner = db.relationship('Partner')
    reports = db.relationship('Report')
    errors = db.relationship('Error')
    task = db.relationship('Task', uselist=False, back_populates='user')


class Partner(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    activation_code = db.Column(db.String(10), unique=True, nullable=False)

    users = db.relationship('User', back_populates='partner')


class Settings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    morning_time = db.Column(db.DateTime, default=partial(datetime.datetime, 2018, 1, 1, 7, 0))
    evening_time = db.Column(db.DateTime, default=partial(datetime.datetime, 2018, 1, 1, 18, 0))
    delta = db.Column(db.Interval, default=partial(datetime.timedelta, minutes=15))
    motivation_time = db.Column(db.DateTime, default=partial(datetime.datetime, 2018, 1, 1, 14, 0))
    bot_expired_on = db.Column(db.DateTime, default=partial(datetime.datetime, 2018, 11, 24, 0, 0))


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    completed = db.Column(db.Boolean, default=False)
    motivation = db.Column(db.Text, nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', back_populates='task')


class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', back_populates='reports')


class Error(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', back_populates='errors')
