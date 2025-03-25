from telethon import TelegramClient
from telethon.tl.functions.contacts import ImportContactsRequest
from telethon.tl.types import InputPhoneContact
import os
from .models import Celular, MensajeEnviado
from .database import db

def obtener_credenciales(id_celular):
    return Celular.query.filter_by(id=id_celular).first()

def guardar_mensaje(numero, usuario, mensaje, titulo):
    nuevo_mensaje = MensajeEnviado(numero=numero, usuario=usuario, mensaje=mensaje, titulo=titulo)
    db.session.add(nuevo_mensaje)
    db.session.commit()

async def enviar_mensaje(id_celular, destinatario, mensaje, titulo):
    credencial = obtener_credenciales(id_celular)
    if not credencial:
        return {"status": "error", "message": "No se encontraron credenciales"}

    numero = credencial.numero
    api_id = credencial.app_id
    api_hash = credencial.api_hash

    session_path = f"session/{numero.replace('+', '')}.session"
    os.makedirs("session", exist_ok=True)
    client = TelegramClient(session_path, api_id, api_hash)

    await client.start(numero)

    contact = InputPhoneContact(client_id=0, phone=destinatario, first_name=destinatario, last_name="")
    result = await client(ImportContactsRequest([contact]))

    if result.users:
        user = result.users[0]
        await client.send_message(user.id, mensaje)
        guardar_mensaje(numero, destinatario, mensaje, titulo)
        await client.disconnect()
        return {"status": "success", "message": f"Mensaje enviado a {destinatario}"}
    else:
        await client.disconnect()
        return {"status": "error", "message": "No se pudo encontrar el usuario en Telegram"}