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
        #file["arrived"]="NO"
        file.to_csv(os.path.join("./project/comps/", name, "competitors"), index_label='ID')#save file
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
    return 'comp_page'

@main.route('/edit_comp')
@login_required
def edit_comp():
    compname = str(request.args.get('comp'))
    data = pandas.read_csv(os.path.join('./project/comps/', compname, 'competitors'))
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
    data = pandas.read_csv(os.path.join('./project/comps/', compname, 'competitors'), index_col='ID')
    #data = pandas.DataFrame(data)
    print(id, data)
    data.drop(id).to_csv(os.path.join('./project/comps/', compname, 'competitors'))
    #data.save(os.path.join('./project/comps/', compname, 'competitors'))
    #print(data)
    return redirect(url_for('main.edit_comp', comp = compname))


@main.route('/change_prsn_state', methods=['POST'])
@login_required
def change_prsn_state():
    try:
        data = request.json
        id = data.get('id')
        compname = data.get('compname')
        print(id, compname)
        df = pandas.read_csv(os.path.join('./project/comps/', compname, 'competitors'), index_col=False)
        print(df.loc[int(id), 'Name'])
        if df.loc[int(id), "Paid"] == 'YES': 
            df.loc[int(id), "Paid"] = 'NO' 
        else:
            df.loc[int(id), "Paid"] = 'YES'
        print(df)
        df.to_csv(os.path.join('./project/comps/', compname, 'competitors'), index=False)
    except Exception as e:
        print(e)

    
    return "ok"