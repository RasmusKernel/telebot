from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from shared.Config import MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB

db = SQLAlchemy()

def init_db(app: Flask):
    app.config["SQLALCHEMY_DATABASE_URI"] = (
        f"mysql+mysqlconnector://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}/{MYSQL_DB}"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)
    with app.app_context():
        db.create_all()
