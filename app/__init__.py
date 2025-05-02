from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os
from dotenv import load_dotenv
load_dotenv()
from datetime import datetime
import pytz


db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")
    
    DB_NAME = os.getenv("DB_NAME")
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")

    app.config['SQLALCHEMY_DATABASE_URI'] = (
        f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    login_manager.init_app(app)

    login_manager.login_view = 'main.login'

    from .routes import main
    app.register_blueprint(main)

    @app.template_filter('localtime')
    def localtime_filter(utc_dt):
        local_tz = pytz.timezone("Asia/Tbilisi") 
        return utc_dt.replace(tzinfo=pytz.utc).astimezone(local_tz).strftime('%d/%m/%Y %H:%M')

    with app.app_context():
        db.create_all()

    return app

from .models import User
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))