from . import db
from flask_login import UserMixin

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))

class Competitor(db.Model):
    id = db.Column(db.Integer, primary_key = True, autoincrement='auto')
    competition_id = db.Column(db.Integer, db.ForeignKey('competition.id'))#id of competition attended by competitor
    name = db.Column(db.String(100))
    comp_id = db.Column(db.Integer)#id of competitor during competition
    event_1 = db.Column(db.String(20))
    event_2 = db.Column(db.String(20))
    event_3 = db.Column(db.String(20))
    event_4 = db.Column(db.String(20))


class Competition(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(20))
    event_1 = db.Column(db.String(20))
    event_2 = db.Column(db.String(20))
    event_3 = db.Column(db.String(20))
    event_4 = db.Column(db.String(20))



class Result(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    round_id = db.Column(db.ForeignKey('round.id'))
    round = db.relationship("Round", backref=db.backref("round", uselist=False))
    competitor_id = db.Column(db.ForeignKey('competitor.id'))
    competitor = db.relationship("Competitor", backref=db.backref("competitor", uselist = False))
    first = db.Column(db.String(20), default = "_.__")
    second = db.Column(db.String(20), default = "_.__")
    third = db.Column(db.String(20), default = "_.__")
    fourth = db.Column(db.String(20), default = "_.__")
    fifth = db.Column(db.String(20), default = "_.__")
    ao5 = db.Column(db.String(20), default = "_.__")
    ao5s = db.Column(db.Float, default = 999.00)
    best = db.Column(db.String(20), default = "_.__")

class Round(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    competition_id = db.Column(db.ForeignKey('competition.id'))
    competition = db.relationship("Competition", backref = db.backref("competition", uselist = False))
    stage = db.Column(db.Integer)
