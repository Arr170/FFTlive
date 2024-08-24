from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from sqlalchemy import case, asc
import os, pandas, shutil
from project.results import Result
from . import db
from .models import *




def get_competitions(competition_id=None):
    args = request.args
    
    query = Competition.query


    if competition_id:
        query = query.filter_by(id=competition_id)

    competitions = query.all()


    return competitions_schema.jsonify(competitions)

    

def get_competitors(competitor_id=None, competition_id=None):
    query = Competitor.query
    if competitor_id:
        query = query.filter_by(id=competitor_id)
        competitor = query.first()
        return competitor_schema.jsonify(competitor)
    if competition_id:
        query = query.filter_by(competition_id=competition_id)    
    competitors = query.all()
    return competitors_schema.jsonify(competitors)



def get_events(event_name=None):
    query = Event.query
    if event_name:
        query = query.filter_by(name=event_name)
        events = query.first()
        return events_schema.jsonify(events)
    else:
        events = query.all()
        return events_schema.jsonify(events)

def get_rounds(competition_id=None, event_id=None, number=None, id=None):
    args = request.args

    query = Round.query


    if competition_id:
        query = query.filter_by(competition_id=competition_id)
    
    if id:
        query = query.filter_by(id=id)

    if event_id:
        query = query.filter_by(event_id=event_id)

    if number:
        query = query.filter_by(number = number)
    rounds = query.all()

    return rounds_schema.jsonify(rounds)




def get_averages(round_id=None, competitor_id=None, competition_id=None, id=None):
    args = request.args

    query = Average.query

    
    if id:
        query = query.filter_by(id=id)

    if round_id:
        query = query.filter_by(round_id=round_id)

    if competitor_id:
        query = query.filter_by(competitor_id=competitor_id)

    if competition_id:
        query = query.filter_by(competition_id=competition_id)

    avgs = query.order_by(
            case(
                (Average.avg == None, 1),
            else_=0
            ),
            asc(Average.avg)
            ).order_by(
            case(
                (Average.best == None, 1),
                else_=0
            ),
            asc(Average.best)
        ).all()


    return averages_schema.jsonify(avgs)

def get_competition_events():
    competition_events = CompetitionEvent.query.all()
    return jsonify([{'competition_id': ce.competition_id, 'event_id': ce.event_id} for ce in competition_events])

