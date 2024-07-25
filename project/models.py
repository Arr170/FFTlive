from . import db
from flask_login import UserMixin


competitor_events = db.Table('competitor_events', 
    db.Column('Competitor_id', db.Integer, db.ForeignKey('competitor.id'), primary_key=True),
    db.Column('Event_id', db.Integer, db.ForeignKey('event.id'), primary_key=True)
    )

competitions_events = db.Table('competitions_events', 
    db.Column('Competition_id', db.Integer, db.ForeignKey('competition.id'), primary_key=True),
    db.Column('Event_id', db.Integer, db.ForeignKey('event.id'), primary_key=True)
    )

round_competitors = db.Table('competitor_rounds', 
    db.Column('Competitor_id', db.Integer, db.ForeignKey('competitor.id'), primary_key=True),
    db.Column('Round_id', db.Integer, db.ForeignKey('round.id'), primary_key=True)
    )
            

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))



class Competitor(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    # own
    name = db.Column(db.String(100))
    # foreign
    competition_id = db.Column(db.Integer, db.ForeignKey('competition.id'), nullable=False)

    events = db.relationship('Event', secondary=competitor_events, backref=db.backref('competitors', lazy=True))

class Competition(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String)
    # relation
    events = db.relationship('Event', secondary=competitor_events, backref=db.backref('competitions', lazy=True))

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    format = db.Column(db.String(3)) # ao5/mo3

class Result(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.Integer)
    #foreign
    competitor_id = db.Column(db.Integer, db.ForeignKey('competitor.id'), nullable=False)
    round_id = db.Column(db.Integer, db.ForeignKey('round.id'), nullable=False)

class Average(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    # own
    first = db.Column(db.Integer, db.ForeignKey('result.id')) 
    second = db.Column(db.Integer, db.ForeignKey('result.id'))  
    third = db.Column(db.Integer, db.ForeignKey('result.id')) 
    fourth = db.Column(db.Integer, db.ForeignKey('result.id'))  
    fifth = db.Column(db.Integer, db.ForeignKey('result.id')) 
    avg = db.Column(db.Integer)
    best = db.Column(db.Integer)
    # foreign
    

class Round(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # own
    number = db.Column(db.Integer, nullable = False)
    # foreign
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    competition_id = db.Column(db.Integer, db.ForeignKey('competition.id'), nullable = False)
    # relations
    competitors = db.relationship('Competitor', secondary=round_competitors, 
                                    backref=db.backref('rounds', lazy=True))
