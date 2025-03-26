from flask_sqlalchemy import SQLAlchemy
from flask import Flask
import src.shared.Config as config

db = SQLAlchemy()

def init_db(app: Flask):
    app.config["SQLALCHEMY_DATABASE_URI"] = f"mysql+mysqlconnector://{config.MYSQL_USER}:{config.MYSQL_PASSWORD}@{config.MYSQL_HOST}/{config.MYSQL_DB}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)
    with app.app_context():
        db.create_all()
