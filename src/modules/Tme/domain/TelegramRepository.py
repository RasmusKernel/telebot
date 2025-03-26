from src.modules.Tme.domain.Telegram import Celular, MensajeEnviado
from src.shared.database.Database import db

class TelegramRepository:
    @staticmethod
    def obtener_credenciales(id_celular):
        return Celular.query.filter_by(id=id_celular).first()

    @staticmethod
    def guardar_mensaje(numero, usuario, mensaje, titulo):
        nuevo_mensaje = MensajeEnviado(numero=numero, usuario=usuario, mensaje=mensaje, titulo=titulo)
        db.session.add(nuevo_mensaje)
        db.session.commit()
