from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
import os, pandas
from project.results import Result
from . import db
from .models import Competition, Competitor, Result, Round
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, select, update, delete




main = Blueprint('main', __name__)

if(os.environ['IS_PROD']=='1'):
    COMP_PATH = '/project/comps'
else:
    COMP_PATH = './project/comps'

engine = create_engine('sqlite:///' + os.path.join(os.getcwd(),COMP_PATH, 'users.db'))



@main.route('/', methods=['GET'])#db
def competitions():
    df = pandas.read_sql(select(Competition).order_by(Competition.id), con=engine )
    comp_list=df[["name", "id"]].to_dict('records')
    print(comp_list)
    return render_template('competitions.html', comps = comp_list)

@main.route('/competitions', methods=['POST'])#db
@login_required
def competitions_post():
    try:
        name = str(request.form.get('compname'))
        file = request.files['csvfile']
        if os.path.splitext(file.filename)[-1] != '.csv':#check for file extention
            flash('Wrong file format!')
            return redirect(url_for('main.competitions'))
        df = pandas.read_sql(select(Competition).order_by(Competition.id), con=engine )
        df = pandas.read_csv(file)
        cols = []
        for col in df: cols.append(col)#column names
        print("column num", len(cols))
        if len(cols) != 5:
            flash('Wrong number of columns in file!')
            return redirect(url_for('main.competitions'))
        
        new_comp = Competition(name=name, event_1 = cols[1], event_2=cols[2], event_3=cols[3], event_4=cols[4])
        db.session.add(new_comp)
        db.session.commit()
        df = df.to_dict('records')
        new_comp_id = new_comp.id
        for i, row in enumerate(df):
            new_competitor = Competitor(name=row[cols[0]], competition_id = new_comp_id, comp_id=i, event_1=row[cols[1]], event_2=row[cols[2]], event_3=row[cols[3]], event_4=row[cols[4]])
            db.session.add(new_competitor)
            db.session.commit()
    except Exception as e:
        print(e)
        flash('Something went wrong!')

    return redirect(url_for('main.competitions'))
    
@main.route('/dlt_comp', methods=['POST'])#db
@login_required
def dlt_comp():
    id = request.args.get('id')
    print("id",id)
    Competition.query.filter_by(id=id).delete()
    db.session.commit()

    return redirect(url_for('main.competitions'))

@main.route('/comp_page')
def comp_page():
    id = request.args.get('id')
    competition = pandas.read_sql(select(Competition).where(Competition.id==id), con=engine)
    rounds = pandas.read_sql(select(Round).where(Round.competition_id==id), con=engine)
    
    return render_template('comp_page.html')

@main.route('/edit_comp')#
@login_required
def edit_comp():
    id = request.args.get('id')
    q = select(Competitor).where(Competitor.competition_id==id)
    df = pandas.read_sql(q, con=engine)
    competition = pandas.read_sql(select(Competition).where(Competition.id==id), con=engine)
    cols = ["ID", "Name", competition.event_1.values[0], competition.event_2.values[0], competition.event_3.values[0], competition.event_4.values[0]]#column names
    dict_ = df.to_dict('split')
    
    return render_template('comp_edit.html', cols = cols, rows = dict_['data'], competition_id = id)

@main.route('/dlt_person', methods=['POST'])#deleting person from csv
@login_required
def dlt_person():
    id=int(request.args.get('id'))
    compname = request.args.get('compname')
    df = pandas.read_csv(os.path.join(COMP_PATH, compname, 'competitors.csv'), index_col="ID")
    print(df.index)
    new = df.drop(int(id))
    new.to_csv(os.path.join(COMP_PATH, compname, 'competitors.csv'))

    return redirect(url_for('main.edit_comp', comp = compname))


@main.route('/change_prsn_state', methods=['POST'])#changing state of paid indicator
@login_required
def change_prsn_state():
    try:
        data = request.json
        id = data.get('id')
        compname = data.get('compname')
        df = pandas.read_csv(os.path.join(COMP_PATH, compname, 'competitors.csv'), index_col=False)
        person = df[df["ID"]==int(id)]
        #print(df[['Name', "ID", 'Paid']][df['ID']==int(id)],'\n',person['Paid'].values)
        if person['Paid'].values == 'YES': 
            df.loc[df["ID"]==int(id), 'Paid'] = 'NO' 
        else:
            df.loc[df["ID"]==int(id), 'Paid'] = 'YES'
        df.to_csv(os.path.join(COMP_PATH, compname, 'competitors.csv'), index=False)
    except Exception as e:
        print('Error',e)

    
    return "ok"

@main.route('/sort_by', methods=['POST'])
@login_required
def sort_by():
    data = request.json
    compname = data.get('compname')
    label = data.get('label')
    df=pandas.read_csv(os.path.join(COMP_PATH, compname, 'competitors.csv'), index_col=False)
    df = df.sort_values(by=label)
    df.to_csv(os.path.join(COMP_PATH, compname, 'competitors.csv'), index=False)

    return "ok"

@main.route('/make_event', methods=["POST"])#makam na tomlhe ted
@login_required
def make_event():
    try:
        data = request.json
        id = data.get('id')
        name = data.get('name')
        new_round = Round(name=name, competition_id = id, stage=1)
        db.session.add(new_round)
        competitors = pandas.read_sql(select(Competition))


    except Exception as e:
        print('Error:', e)
        return e
        
    return "ok"

@main.route('/create_groups', methods=['POST'])
@login_required
def create_groups():
    data = request.json
    compname = data.get('compname')
    event = data.get('event')
    round = data.get('round')
    round_df = pandas.read_csv(os.path.join(COMP_PATH, compname, event, round+'.csv'))
    groups_df = round_df[['ID', 'Name']]
    groups_df['Group'] = 0
    count = len(groups_df)
    if(count < 25):
        groups_df.loc[0:count/2, 'Group'] = 1
        groups_df.loc[count/2:count, 'Group'] = 2
    else:
        groups_df.loc[0:count/3, 'Group'] = 1
        groups_df.loc[count/3:count*2/3, 'Group'] = 2
        groups_df.loc[count*2/3:count, 'Group'] = 3
    print(groups_df)
    groups_df.to_csv(os.path.join(COMP_PATH, compname, event, round+' groups'+'.csv'))

    return "ok"

@main.route('/round_page', methods=['GET'])
def round_page():
    compname = request.args.get('compname')
    event = request.args.get('event')
    round = request.args.get('round')
    data = pandas.read_csv(os.path.join(COMP_PATH, compname, event, round+'.csv'))    
    cols = []
    data.insert(0, 'pos', range(1, 1 + len(data)))
    for col in data: cols.append(col)
    dict_ = data.to_dict('split')

    return render_template('round_page.html', cols = cols, rows = dict_['data'], compname=compname, event=event, round=round)

@main.route('/groups', methods=['GET'])
def groups():
    compname = request.args.get('compname')
    event = request.args.get('event')
    round = request.args.get('round')
    data = pandas.read_csv(os.path.join(COMP_PATH, compname, event, round+'.csv'))    
    cols = []
    for col in data: cols.append(col)
    dict_ = data.to_dict('split')

    return render_template('groups.html', cols = cols, rows = dict_['data'], compname=compname, event=event, round=round)

@main.route('/enter_results', methods=['GET', 'POST'])
@login_required
def enter_results():
    if request.method == 'GET':
        #getting data for table
        compname = request.args.get('compname')
        event = request.args.get('event')
        round = request.args.get('round')
        df = pandas.read_csv(os.path.join(COMP_PATH, compname, event, round+'.csv'))
        df.insert(0, 'pos', range(1, 1 + len(df)))
        cols = []        
        for col in df: cols.append(col)
        dict_ = df.to_dict('split')
        return render_template('enter_results.html', cols = cols, rows = dict_['data'], compname=compname, event=event, round = round)
    if request.method == 'POST':
        data = request.form
        name = data.get('input_name')
        id = data.get('input_id')
        first = data.get('input_solve1')
        second = data.get('input_solve2')
        third = data.get('input_solve3')
        fourth = data.get('input_solve4')
        fifth = data.get('input_solve5')
        compname = data.get('compname')
        event = data.get('event')
        round = data.get('round')
        df = pandas.read_csv(os.path.join(COMP_PATH, compname, event, round+'.csv'), index_col=False)
        result = Result(first, second, third, fourth, fifth)
        df.loc[df["ID"]==int(id), '1'] = str(first)
        df.loc[df["ID"]==int(id), '2'] = str(second)
        df.loc[df["ID"]==int(id), '3'] = str(third)
        df.loc[df["ID"]==int(id), '4'] = str(fourth)
        df.loc[df["ID"]==int(id), '5'] = str(fifth)
        df.loc[df["ID"]==int(id), 'Best'] = str(result.best_solve)
        df.loc[df["ID"]==int(id), 'Ao5'] = str(result.formated(result.result))
        df.loc[df["ID"]==int(id), 'Ao5s'] = str(result.result)
        df.Ao5s = df.Ao5s.astype(float)
        df = df.sort_values(['Ao5s','Best'])
        df.to_csv(os.path.join(COMP_PATH, compname, event, round+'.csv'), index=False)

        return "ok"
    
@main.route('/make_next', methods=['POST'])
@login_required
def make_next():
    data = request.json
    compname = data.get('compname')
    event = data.get('event')
    round = data.get('round')
    num = int(data.get('num'))
    df = pandas.read_csv(os.path.join(COMP_PATH, compname, event, round+'.csv'), index_col=False)
    df.loc[:(num-1), 'to_next'] = True
    df.to_csv(os.path.join(COMP_PATH, compname, event, round+'.csv'), index=False)
    last = int(num)
    new_df=df.head(last)
    new_df[["1", "2", "3", "4", "5", "Best", "Ao5"]] = '__._' #Ao5 is for storing in seconds
    new_df["Ao5s"]=999
    new_df["to_next"]=False 
    new_df.to_csv(os.path.join(COMP_PATH, compname, event, str(int(round)+1)+'.csv'), index=False)
    return 'ok'

@main.route('/delete_from_round', methods=['POST'])
@login_required
def delete_from_round():
    data = request.json
    compname = data.get('compname')
    event = data.get('event')
    round = data.get('round')
    id = int(data.get('id'))
    df = pandas.read_csv(os.path.join(COMP_PATH, compname, event, round+'.csv'), index_col='ID')
    df.drop(id).to_csv(os.path.join(COMP_PATH, compname, event, round+'.csv'))
    return 'ok'
    
@main.route('/new_competitor_round', methods=['POST'])
@login_required
def new_competitor_round():
    data = request.json
    id = data.get('ID')
    name = data.get('Name')
    compname = data.get('compname')
    event = data.get('event')
    round = data.get('round')
    df = pandas.read_csv(os.path.join(COMP_PATH, compname, event, round+'.csv'), index_col=False)
    add_df = pandas.DataFrame([[id, name, '__._', '__._', '__._', '__._', '__._', '__._', '__._', 999.0, False]], columns=['ID', 'Name', '1', '2', '3', '4', '5', 'Best', 'Ao5', 'Ao5s', 'to_next'])
    df = pandas.concat([df,add_df], ignore_index=True)
    df.to_csv(os.path.join(COMP_PATH, compname, event, round+'.csv'), index=False)
    return "ok"

@main.route('/new_competitor_comp', methods=['POST'])
@login_required
def new_competitor_comp():
    data = request.json
    print(data)
    event_1 = 'Ano' if data.get('event_1') else 'Ne'
    event_2 = 'Ano' if data.get('event_2') else 'Ne'
    event_3 = 'Ano' if data.get('event_3') else 'Ne'
    event_4 = 'Ano' if data.get('event_4') else 'Ne'
    name = data.get('Name')
    print()
    compname = data.get('compname')
    df = pandas.read_csv(os.path.join(COMP_PATH, compname, 'competitors.csv'), index_col=False)
    id = len(df) + 2
    cols = []
    for col in df: cols.append(col)#column names

    add_df=pandas.DataFrame([[id, name, 'Mail', event_1, event_2, event_3, event_4, 'YES']], columns=cols)

    df = pandas.concat([df,add_df], ignore_index=True)
    df.to_csv(os.path.join(COMP_PATH, compname, 'competitors.csv'), index=False)

    return "ok"

@main.route('/name_by_id', methods=['POST'])
@login_required
def name_by_id():
    data = request.json
    id = data.get('ID')
    compname = data.get('compname')
    event = data.get('event')
    round = data.get('round')
    df = pandas.read_csv(os.path.join(COMP_PATH, compname, event, round+'.csv'), index_col=False)
    print(df[df['ID']==int(id)].to_json(orient='records'))
    return df[df['ID']==int(id)].to_json(orient='records')


