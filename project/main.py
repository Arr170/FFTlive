from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
import os, pandas
from . import db



main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/profile')
@login_required
def profile():
    return render_template('profile.html', name = current_user.name)

@main.route('/competitions')
def competitions():
    comp_list = os.listdir("./project/comps")
    return render_template('competitions.html', comps = comp_list)

@main.route('/competitions', methods=['POST'])
@login_required
def competitions_post():
    name = str(request.form.get('compname'))
    file = request.files['csvfile']
    comp_list = os.listdir("./project/comps")
    print("name:", name)
    print("filename:", file.filename)
    for comp in comp_list:
        if name == str(comp):
            flash('Competition already exists!')
            return redirect(url_for('main.competitions'))
    ###neco s tim budeme delat###
    os.mkdir(os.path.join("./project/comps/", name))
    pandas.read_csv(file).to_csv(os.path.join("./project/comps/", name, "competitors"), index_label='ID')
    #file.save(os.path.join("./project/comps/", name, "competitors"))

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

@main.route('/dlt_person', methods=['POST'])
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

