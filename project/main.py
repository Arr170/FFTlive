from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
import os, pandas, shutil
from . import db



main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/profile')
@login_required
def profile():
    return render_template('profile.html', name = current_user.name)

@main.route('/competitions', methods=['GET'])
def competitions():
    comp_list = os.listdir("./project/comps")
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
        comp_list = os.listdir("./project/comps")
        for comp in comp_list:#check for existing names
            if name == str(comp):
                flash('Competition already exists!')
                return redirect(url_for('main.competitions'))
        os.mkdir(os.path.join("./project/comps/", name))
        file = pandas.read_csv(file)
        file["Paid"]="NO"
        file['E-mail'] = file['E-mail'].str.lower()
        #file["arrived"]="NO"
        file.to_csv(os.path.join("./project/comps/", name, "competitors.csv"), index_label='ID')#save file
    except Exception as e:
        print(e)
        flash('Something went wrong!')
    #file.save(os.path.join("./project/comps/", name, "competitors"))

    return redirect(url_for('main.competitions'))
    
@main.route('/dlt_comp', methods=['POST'])
@login_required
def dlt_comp():
    compname = request.args.get('compname')
    shutil.rmtree(os.path.join('./project/comps/', compname))
    return redirect(url_for('main.competitions'))

@main.route('/comp_page')
def comp_page():
    compname = str(request.args.get('comp'))
    all = os.listdir(os.path.join("./project/comps", compname))
    events = [entry for entry in all if not entry.endswith('.csv')]
    rounds = []
    for event in events:
        rounds.append(os.listdir(os.path.join('./project/comps/', compname, event)))
    return render_template('comp_page.html', events=events, rounds = rounds)

@main.route('/edit_comp')
@login_required
def edit_comp():
    compname = str(request.args.get('comp'))
    data = pandas.read_csv(os.path.join('./project/comps/', compname, 'competitors.csv'))
    cols = []
    for col in data: cols.append(col)
    dict_ = data.to_dict('split')
    #print(pandas.DataFrame(data))
    return render_template('comp_edit.html', cols = cols, rows = dict_['data'], compname=compname)

@main.route('/dlt_person', methods=['POST'])#deleting person from csv
@login_required
def dlt_person():
    print('delete triggered')
    id=int(request.args.get('id'))
    compname = str(request.args.get('compname'))
    data = pandas.read_csv(os.path.join('./project/comps/', compname, 'competitors.csv'), index_col='ID')
    #data = pandas.DataFrame(data)
    print(id, data)
    data.drop(id).to_csv(os.path.join('./project/comps/', compname, 'competitors.csv'))
    #data.save(os.path.join('./project/comps/', compname, 'competitors'))
    #print(data)
    return redirect(url_for('main.edit_comp', comp = compname))


@main.route('/change_prsn_state', methods=['POST'])#changing state of paid indicator
@login_required
def change_prsn_state():
    try:
        data = request.json
        id = data.get('id')
        compname = data.get('compname')
        df = pandas.read_csv(os.path.join('./project/comps/', compname, 'competitors.csv'), index_col=False)
        person = df[df["ID"]==int(id)]
        #print(df[['Name', "ID", 'Paid']][df['ID']==int(id)],'\n',person['Paid'].values)
        if person['Paid'].values == 'YES': 
            df.loc[df["ID"]==int(id), 'Paid'] = 'NO' 
        else:
            df.loc[df["ID"]==int(id), 'Paid'] = 'YES'
        df.to_csv(os.path.join('./project/comps/', compname, 'competitors.csv'), index=False)
    except Exception as e:
        print('Error',e)

    
    return "ok"

@main.route('/sort_by', methods=['POST'])
@login_required
def sort_by():
    data = request.json
    compname = data.get('compname')
    label = data.get('label')
    df=pandas.read_csv(os.path.join('./project/comps/', compname, 'competitors.csv'), index_col=False)
    df = df.sort_values(by=label)
    df.to_csv(os.path.join('./project/comps/', compname, 'competitors.csv'), index=False)

    return "ok"

@main.route('/make_event', methods=["POST"])
@login_required
def make_event():
    try:
        data = request.json
        compname = data.get('compname')
        label = data.get('label')
        df=pandas.read_csv(os.path.join('./project/comps/', compname, 'competitors.csv'), index_col=False)
        new_df=df[["ID", "Name", label]][df['Paid']=="YES"]
        new_df=new_df[["ID", "Name"]][df[label]=='Ano']
        new_df[["1", "2", "3", "4", "5", "Best", "Ao5"]] = '0.00'
        os.mkdir(os.path.join('./project/comps/', compname, label))
        new_df.to_csv(os.path.join('./project/comps/', compname, label, '1.csv'), index=False)
    except Exception as e:
        print('Error:', e)
        
    return "ok"

