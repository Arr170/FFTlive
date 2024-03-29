from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager


db = SQLAlchemy()

def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = 'a82ead125a1141a6520afa4d9eb3946d1c657af7dcf3e0553433521aa41ba253'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://arzi:at2gYh8Y2YbKJpqS9gFNeNHOz5mxpvYY@dpg-cmrp5na1hbls73fqgpk0-a.frankfurt-postgres.render.com/fftlivedb'

    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        # since the user_id is just the primary key of our user table, use it in the query for the user
        return User.query.get(int(user_id))

    from . import models

    with app.app_context():
        db.create_all()

     # blueprint for auth routes in our app
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    # blueprint for non-auth parts of app
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app
