from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
import os, pandas, shutil
from project.results import Result
from . import db



main = Blueprint('main', __name__)

if(os.environ['IS_PROD']==1):
    COMP_PATH = '/project/comps'
else:
    COMP_PATH = './project/comps'

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/profile')
@login_required
def profile():
    return render_template('profile.html', name = current_user.name)

@main.route('/competitions', methods=['GET'])
def competitions():
    comp_list = os.listdir(COMP_PATH)
    return render_template('competitions.html', comps = comp_list)

@main.route('/competitions', methods=['POST'])
@login_required
def competitions_post():
    
    try:
        name = str(request.form.get('compname'))
        file = request.files['csvfile']
        if os.path.splitext(file.filename)[-1] != '.csv':#check for file extention
            flash('Wrong file format!')
            return redirect(url_for('main.competitions'))
        comp_list = os.listdir(COMP_PATH)
        for comp in comp_list:#check for existing names
            if name == str(comp):
                flash('Competition already exists!')
                return redirect(url_for('main.competitions'))
        os.mkdir(os.path.join("COMP_PATH", name))
        file = pandas.read_csv(file)
        file["Paid"]="NO"
        file['E-mail'] = file['E-mail'].str.lower()
        #file["arrived"]="NO"
        file.to_csv(os.path.join(COMP_PATH, name, "competitors.csv"), index_label='ID')#save file
    except Exception as e:
        print(e)
        flash('Something went wrong!')

    return redirect(url_for('main.competitions'))
    
@main.route('/dlt_comp', methods=['POST'])
@login_required
def dlt_comp():
    compname = request.args.get('compname')
    shutil.rmtree(os.path.join(COMP_PATH, compname))
    return redirect(url_for('main.competitions'))

@main.route('/comp_page')
def comp_page():
    compname = str(request.args.get('comp'))
    all = os.listdir(os.path.join(COMP_PATH, compname))
    events = [entry for entry in all if not entry.endswith('.csv')]
    rounds = []
    for event in events:
        round_list = os.listdir(os.path.join(COMP_PATH, compname, event))
        round_list = [x.split('.')[0] for x in round_list]
        box = [event, round_list]#contains:[event name, array of round numbers]
        rounds.append(box)
    return render_template('comp_page.html', events=events, rounds = rounds, compname=compname)

@main.route('/edit_comp')
@login_required
def edit_comp():
    compname = str(request.args.get('comp'))
    data = pandas.read_csv(os.path.join(COMP_PATH, compname, 'competitors.csv'))
    cols = []
    for col in data: cols.append(col)
    dict_ = data.to_dict('split')
    #print(pandas.DataFrame(data))
    return render_template('comp_edit.html', cols = cols, rows = dict_['data'], compname=compname)

@main.route('/dlt_person', methods=['POST'])#deleting person from csv
@login_required
def dlt_person():
    id=request.args.get('id')
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

@main.route('/make_event', methods=["POST"])
@login_required
def make_event():
    try:
        data = request.json
        compname = data.get('compname')
        label = data.get('label')
        df=pandas.read_csv(os.path.join(COMP_PATH, compname, 'competitors.csv'), index_col=False)
        new_df=df[["ID", "Name", label]][df['Paid']=="YES"]
        new_df=new_df[["ID", "Name"]][df[label]=='Ano']
        new_df[["1", "2", "3", "4", "5", "Best", "Ao5"]] = '__._' #Ao5 is for storing in seconds
        new_df["Ao5s"]=999
        os.mkdir(os.path.join(COMP_PATH, compname, label))
        new_df.to_csv(os.path.join(COMP_PATH, compname, label, '1.csv'), index=False)
    except Exception as e:
        print('Error:', e)
        
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
    last = int(len(df)*num/len(df))
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
    print(data, '############')
    df = pandas.read_csv(os.path.join(COMP_PATH, compname, event, round+'.csv'), index_col=False)
    add_df = pandas.DataFrame([[id, name, '__._', '__._', '__._', '__._', '__._', '__._', '__._', 999.0, False]], columns=['ID', 'Name', '1', '2', '3', '4', '5', 'Best', 'Ao5', 'Ao5s', 'to_next'])
    print(add_df)
    df = pandas.concat([df,add_df], ignore_index=True)
    df.to_csv(os.path.join(COMP_PATH, compname, event, round+'.csv'), index=False)
    return "ok"
