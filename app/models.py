from .database import db

class Celular(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.String(20), unique=True, nullable=False)
    app_id = db.Column(db.Integer, nullable=False)
    api_hash = db.Column(db.String(50), nullable=False)
    nombre = db.Column(db.String(100), nullable=False)

class MensajeEnviado(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.String(20), nullable=False)
    usuario = db.Column(db.String(20), nullable=False)
    mensaje = db.Column(db.Text, nullable=False)
    titulo = db.Column(db.String(255), nullable=False)