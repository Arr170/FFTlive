from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from sqlalchemy import case, asc
import os, pandas, shutil
from project.results import Result
from . import db
from .models import *



api = Blueprint('api', __name__)

# POST:
# data formate: 
# {
#   competition_name: xxxx,
#   events: [
#               {
#                   name: "event name",
#                   number: "number of rounds"
#                   rounds_numbers: [] how many competitor advances to next rounnd. ex: ['70%', '8', '0']
#               }
#           ]
# 
# 
# 
# }
@api.route('/api/competitions', methods=['GET', 'POST'])
def api_get_competitions(competition_id=None):
    if request.method == 'GET':
        args = request.args
        
        query = Competition.query

        if args.__contains__("competition_id"):
            query = query.filter_by(id=args["competition_id"])

        if competition_id:
            query = query.filter_by(id=competition_id)

        competitions = query.all()

        print(competitions)

        return competitions_schema.jsonify(competitions)

    elif request.method == 'POST':
        try:
            data = request.json
            name = data.get('competition_name')
            events = data.get('events')

            check_comp = Competition.query.filter_by(name=name).first()
            if check_comp:
                return {"message": "dublicate name"}, 200

            new_competition = Competition(name=name)
            db.session.add(new_competition)
            db.session.commit()

            for ev in events:
                event = Event.query.filter_by(name = ev["name"]).first()
                if event:
                    new_competition.events.append(event)
                    db.session.commit()
            
                for num in range(1, int(ev["number"])+1):

                    new_round = Round(number = num, event_id = event.id, competition_id = new_competition.id, advances=ev["rounds_numbers"][num-1])
                    db.session.add(new_round)
                    db.session.commit()
                    print("new round added")
            return {"message": "created"}, 201

        except Exception as e:
            print(e)
            flash(str(e))
    else:
        None

@api.route('/api/competitors', methods=["GET"])
def api_get_competitors(competitor_id=None, competition_id=None):
    query = Competitor.query
    if competitor_id:
        query = query.filter_by(id=competitor_id)
        competitor = query.first()
        return competitor_schema.jsonify(competitor)
    if competition_id:
        query = query.filter_by(competition_id=competition_id)    
    competitors = query.all()
    return competitors_schema.jsonify(competitors)



@api.route('/api/competitions/<id>', methods=['PUT', 'DELETE'])
@login_required
def api_competitions_change(id):
    None

@api.route('/api/events', methods=['GET'])
def api_get_events(event_name=None):
    query = Event.query
    if event_name:
        query = query.filter_by(name=event_name)
        events = query.first()
        return events_schema.jsonify(events)
    else:
        events = query.all()
        return events_schema.jsonify(events)

@api.route('/api/rounds', methods=['GET'])
def api_get_rounds(competition_id=None, event_id=None, number=None, id=None):
    args = request.args

    query = Round.query

    if args.__contains__("competition_id"):
        query = query.filter_by(competition_id=args["competition_id"])
    
    if args.__contains__("event_id"):
        query = query.filter_by(event_id=args["event_id"])

    if args.__contains__("number"):
        query = query.filter_by(number = args["number"])

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

@api.route('/api/delete_average/<id>', methods=["DELETE"])
@login_required
def delete_average(id):
    avg = Average.query.get(id)
    db.session.delete(avg)
    db.session.commit()

    return ""



@api.route('/api/averages', methods=['GET'])
def api_get_averages(round_id=None, competitor_id=None, competition_id=None, id=None):
    args = request.args

    query = Average.query

    # if args.__contains__("competition_id"):
    #     query = query.filter_by(competition_id=args["competition_id"])
    
    # if args.__contains__("event_id"):
    #     query = query.filter_by(event_id=args["event_id"])

    if args.__contains__("round_id"):
        query = query.filter_by(round_id=args["round_id"])

    if args.__contains__("average_id"):
        query = query.filter_by(id=args["average_id"])
    
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

@api.route('/api/competition_events', methods=['GET'])
def get_competition_events():
    competition_events = CompetitionEvent.query.all()
    return jsonify([{'competition_id': ce.competition_id, 'event_id': ce.event_id} for ce in competition_events])

