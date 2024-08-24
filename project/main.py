from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
import os, pandas, shutil
from . import db
from .models import *
from .get_funcs import *
import requests



main = Blueprint('main', __name__)

if(os.environ['IS_PROD']=='1'):
    COMP_PATH = '/project/comps'
else:
    COMP_PATH = './project/comps'


@main.route('/', methods=['GET'])
def index():
    comp_list = os.listdir(COMP_PATH)
    return render_template('index.html')

@main.route('/competition', methods=['GET'])
def competition():
    return render_template('competition.html')

@main.route('/competitions', methods=['GET']) #for htmx
def competitions():
    data = get_competitions()
    print(data.json)
    return render_template("competitions.html", data=data.json) #for htmx

@main.route('/navbar_events/<compId>',  methods=["GET"])
def get_navbar_events(compId):
    data = get_competitions(compId)
    print(data.json)
    return render_template("events_bar.html", competition = data.json)

@main.route('/result_tables', methods=["GET"]) # for htmx
def get_result_tables():
    args = request.args
    if args.__contains__("competition_id") and args.__contains__("event_id"):
        rounds = get_rounds(competition_id=args["competition_id"], event_id=args["event_id"])
        return render_template("result_tables.html", rounds=rounds.json)
    return "not enough data", 418

@main.route('/result_table/<id>', methods=['GET'])
def get_round_table(id): # round id
    averages = get_averages(id) 
    r = get_rounds(id=id).json[0]
    advances = r['advances']
    if advances.find("%") != -1:        
        competitors = len(averages.json)
        advances = int(competitors*int(advances[:-1])/100)
    else:
        advances = int(advances)
    return render_template("result_table.html", avgs=averages.json, round = r, adv = advances)

@main.route('/result_table_admin/<id>', methods=['GET'])
@login_required
def get_round_table_admin(id): # round id
    averages = get_averages(id) 
    r = get_rounds(id=id).json[0]
    advances = r['advances']
    if advances.find("%") != -1:        
        competitors = len(averages.json)
        advances = int(competitors*int(advances[:-1])/100)
    else:
        advances = int(advances)
    return render_template("result_table_admin.html", avgs=averages.json, round = r, adv = advances)

@main.route('/results_entering/<id>', methods=['GET'])
def get_results_entering(id, avg=None): # round id
    args = request.args
    if args.__contains__("avg_id"):
        avg = get_averages(id=args.get('avg_id'))
        return render_template("results_entering.html", id=id, average = avg.json[0])
    if args.__contains__("competitor_id"):
        avg = get_averages(round_id=id, competitor_id=args.get('competitor_id'))
        return render_template("results_entering.html", id=id, average = avg.json[0])
    return render_template("results_entering.html", id=id, average = avg)

@main.route('/result_table_entering_on/<id>', methods=["GET"]) # turning on and off results entering form next to result table 
def entering_on(id): # round id
    return render_template("result_table_entering_on.html", round=id)


@main.route('/result_table_entering_off/<id>', methods=["GET"]) # turning on and off results entering form next to result table 
def entering_off(id): # round id
    return render_template("result_table_entering_off.html", round=id)

@main.route("/comp_events/<id>", methods=["GET"]) # pupulating competition's events in modal for adding new competitors
def comp_events(id): # competition id
    comp = get_competitions(competition_id=id)
    return render_template("comp_events.html", competition=comp.json)

@main.route("/add_new_competitor/<id>", methods=["POST"])
@login_required
def add_new_competitor(id): # competition id
    data = request.form
    person = Person.query.filter_by(name=data.get("NewCompetitorName")).first()
    print(person)
    if not person:
        person = Person(name=data.get("NewCompetitorName"))
        db.session.add(person)
        db.session.commit()
        print("PERSON:")
        print(person)

    new_competitor = Competitor(name=data.get("NewCompetitorName"), competition_id=id, person_id = person.id)
    db.session.add(new_competitor)
    db.session.commit()
    for a in data:
        if data.get(a) == "on":
            event = Event.query.filter_by(name = a).first()
            if event:
                new_competitor.events.append(event)
                db.session.commit()
                first_round = get_rounds(competition_id=id, event_id=event.id, number=1).json
                first_round = first_round[0]
                try:
                    new_average = Average(competitor_id = new_competitor.id, round_id = first_round['id'], event_id=event.id, person_id=new_competitor.person_id)
                    db.session.add(new_average)
                    db.session.commit()
                    print("new average added", new_average.id, first_round['id'])
                except Exception as e:
                    print("round may not exist", str(e))
    

    return render_template("add_new_competitor_form.html", compId=id)

@main.route('/results_upload/<id>', methods=["POST"])
@login_required
def results_upload(id): # round id
    rnd = Round.query.get(id)
    data = request.form
    competitor_id = data.get('input_id')
    competitor = Competitor.query.get(competitor_id)

    new_first_time_str = data.get('input_solve1')
    new_first = Result(time_string = new_first_time_str, round_id = id, competitor_id = competitor_id, event_id=rnd.event_id, person_id = competitor.person_id, competition_id=competitor.competition_id)
    db.session.add(new_first)    

    new_second_time_str = data.get('input_solve2')
    new_second = Result(time_string = new_second_time_str, round_id = id, competitor_id = competitor_id, event_id=rnd.event_id, person_id = competitor.person_id, competition_id=competitor.competition_id)
    db.session.add(new_second)

    new_third_time_str = data.get('input_solve3')
    new_third = Result(time_string = new_third_time_str, round_id = id, competitor_id = competitor_id, event_id=rnd.event_id, person_id = competitor.person_id, competition_id=competitor.competition_id)
    db.session.add(new_third)

    new_fourth_time_str = data.get('input_solve4')
    new_fourth = Result(time_string = new_fourth_time_str, round_id = id, competitor_id = competitor_id, event_id=rnd.event_id, person_id = competitor.person_id, competition_id=competitor.competition_id)
    db.session.add(new_fourth) 

    new_fifth_time_str = data.get('input_solve5')
    new_fifth = Result(time_string = new_fifth_time_str, round_id = id, competitor_id = competitor_id, event_id=rnd.event_id, person_id = competitor.person_id, competition_id=competitor.competition_id)
    db.session.add(new_fifth)

    db.session.commit()

    solves_ids=[new_first.id, new_second.id, new_third.id, new_fourth.id, new_fifth.id]
   
    

    average = Average.query.filter_by(round_id=id, competitor_id=competitor_id).first()
    average.append_results(solves_ids)
    db.session.commit()
    return render_template("results_entering.html", id=id, average=None)


@main.route('/person_result/<id>', methods=["GET"])
def person_result(id): # avg id
    result = get_averages(id=id)
    print(result.json)
    return render_template("person_result_modal.html", avg=result.json[0])

@main.route("/competition_competitors/<id>", methods=["GET"])
def competition_competitors(id): # competition id
    competitors = get_competitors(competition_id=id)
    return render_template("competition_competitors.html", cmptrs = competitors.json)
@main.route("/groups/<id>", methods=["get"])
def groups(id): # round id
    averages = Average.query.filter_by(round_id = id).order_by(Average.group).all()
    return render_template("groups_table.html", avgs = averages)

@main.route("/asign_groups/<id>")
@login_required
def asign_groups(id): # round id
    averages = Average.query.filter_by(round_id=id).order_by(Average.id).all()
    counter = 1
    if len(averages) > 20:
        group_count = 3
    else:
        group_count = 2
    
    for av in averages:
        av.group = counter
        counter +=1
        if counter > group_count:
            counter = 1
    db.session.commit()
    return "ok", 200

@main.route("/populate_next_round/<id>", methods=["GET"])
@login_required
def populate_next_round(id):

    averages = get_averages(round_id=id).json
    finished_round = Round.query.filter_by(id=id).first()
    next_round = Round.query.filter_by(competition_id=finished_round.competition_id, event_id=finished_round.event_id, number=(finished_round.number +1)).first()
    if next_round:
        next_avgs = Average.query.filter_by(round_id=next_round.id).all()
        if next_avgs:
            for avg in next_avgs:
                db.session.delete(avg)
            db.session.commit()
        advances = finished_round.advances
        if advances.find("%") != -1:        
            competitors = len(averages)
            advances = int(competitors*int(advances[:-1])/100)
        else:
            advances = int(advances)
        print("IN POPULATING NEXT")
        #print(averages)
        for pos in range(0, advances):
            # print(pos)
            # print(averages[pos]["id"])
            # print(averages[pos]["competitor"]["id"])
            new_avg = Average(competitor_id=averages[pos]["competitor"]["id"], round_id=next_round.id, event_id=next_round.event_id)
            db.session.add(new_avg)
            db.session.commit()
    return "ok", 200

@main.route('/delete_competitor/<id>', methods=["DELETE"])
@login_required
def delete_competitor(id): # competitor id
    competitor_to_delete = Competitor.query.get(id)
    averages_to_delete = Average.query.filter_by(competitor_id=id).all()
    for avg in averages_to_delete:
        db.session.delete(avg)
    db.session.delete(competitor_to_delete)
    db.session.commit()
    return ""

@main.route('/rankings', methods=["GET"])
def rankings():
    events = get_events().json
    return render_template('rankings.html', events = events)

@main.route('/ranking_event_table/<id>', methods=["GET"])
def ranking_event_table(id): # event id
    print("NEW EVENT RATING")
    singles = Result.query.filter_by(record=True, event_id=id).order_by(Result.time).all()
    averages = Average.query.filter_by(record = True, event_id=id).order_by(Average.avg).all()
    print(singles)
    print(averages)

    return render_template("ranking_event_table.html", singles = singles, averages = averages)

@main.route('/events', methods=['GET'])
def api_get_events():
    query = Event.query
    events = query.all()
    return events_schema.jsonify(events)

### old code below ###

###                ###

###                ###
######################
