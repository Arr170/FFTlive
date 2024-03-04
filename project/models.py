from . import db
from flask_login import UserMixin

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))

# class Competitior(db.Model):
#     id = db.Column(db.Integer, primary_key = True)
#     email = db.Column(db.String(100))
#     name = db.Column(db.String(100))
#     comp_id = db.Colimn(db.Interger)

# class Competition(db.Model):
#     id = db.Column(db.Integer, primary_key = True)
#     name = db.Column(db.String)
#     event_1 = db.Column(db.String(20))
#     event_2 = db.Column(db.String(20))
#     event_3 = db.Column(db.String(20))
#     event_4 = db.Column(db.String(20))



# class Result(db.Model):
#     id = db.Column(db.Integer, primary_key = True)
#     competor_id = db.Comlumn()


