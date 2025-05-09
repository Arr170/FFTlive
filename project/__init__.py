from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_cors import CORS, cross_origin
from flask_marshmallow import Marshmallow
from marshmallow import fields
from werkzeug.security import generate_password_hash, check_password_hash
from flask_migrate import Migrate

import os

events = [["3x3x3", "ao5"], ["2x2x2", "ao5"], ["Pyraminx", "ao5"], ["4x4x4", "ao5"], ["Skewb", "ao5"], ["TeamBLD", "ao5"], ["MirrorBlock", "ao5"], ["TeamSolve", "ao5"], ["Clock", "ao5"]]

db = SQLAlchemy()

ma = Marshmallow()


if(os.environ['IS_PROD']=='1'):
    COMP_PATH = '/project/comps'#upravit podle umisteni na servru
else:
    COMP_PATH = './project/data'

def create_app():
    app = Flask(__name__, static_folder='static', template_folder='templates')

    app.config['SECRET_KEY'] = 'a82ead125a1141a6520afa4d9eb3946d1c657af7dcf3e0553433521aa41ba253'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(os.getcwd(),COMP_PATH, 'users.db')

    db.init_app(app)
    ma.init_app(app)
    cors = CORS(app)

    migrate = Migrate(app, db)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    from .models import User, Event, Competition

    @login_manager.user_loader
    def load_user(user_id):
        # since the user_id is just the primary key of our user table, use it in the query for the user
        return User.query.get(int(user_id))

    from . import models

    with app.app_context():
        db.create_all()
    
        user = User.query.filter_by(email = os.environ["ADMIN_MAIL"]).first() # aby nevznikala chyba pri opakovanem zpusteni stranky bez mazani db

        if not user: 
            
            init_admin = User(email = os.environ["ADMIN_MAIL"], name = "Admin",password=generate_password_hash(os.environ["ADMIN_PASS"], method='pbkdf2:sha1') )
            db.session.add(init_admin)
            db.session.commit()
        else:
            user.password = generate_password_hash(os.environ["ADMIN_PASS"])
            db.session.commit()


        for ev in events:
            event = Event.query.filter_by(name=ev[0]).first()
            if not event:
                print("adding new event")
                new_event = Event(name=ev[0], comp_format=ev[1])
                db.session.add(new_event)
                db.session.commit()
        
        # competition = Competition.query.filter_by(name="TEST3").first()

        # if not competition:
        #     new_competition = Competition(name="TEST3")
        #     db.session.add(new_competition)
        #     db.session.commit()

        #     for x in range(0,4):
        #         print("adding event to comp")
        #         event = Event.query.get(x)
        #         if event:
        #             print(event)
        #             new_competition.events.append(event)
        #             db.session.commit()
        # else:
        #     print(competition.name)
        #     print(competition.events)

     # blueprint for auth routes in our app
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    # blueprint for non-auth parts of app
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .api import api as api_blueprint
    app.register_blueprint(api_blueprint)

    return app
