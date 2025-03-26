import os
import asyncio
from telethon import TelegramClient
from telethon.tl.functions.contacts import ImportContactsRequest
from telethon.tl.types import InputPhoneContact
from modules.Tme.infrastructure.Telegram_Model import Celular, MensajeEnviado
from shared.database.Database import db

# Cache para almacenar temporalmente el phone_code_hash
phone_code_cache = {}

async def enviar_mensaje(id_celular, destinatario, mensaje, titulo):
    # Obtenemos las credenciales desde la BD
    credencial = Celular.query.filter_by(id=id_celular).first()
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

def guardar_mensaje(numero, usuario, mensaje, titulo):
    nuevo_mensaje = MensajeEnviado(numero=numero, usuario=usuario, mensaje=mensaje, titulo=titulo)
    db.session.add(nuevo_mensaje)
    db.session.commit()

async def iniciar_sesion_async(numero, api_id, api_hash):
    session_path = f"session/{numero.replace('+', '')}.session"
    os.makedirs("session", exist_ok=True)
    client = TelegramClient(session_path, api_id, api_hash)
    await client.connect()
    if not await client.is_user_authorized():
        code_request = await client.send_code_request(numero)
        phone_code_cache[numero] = code_request.phone_code_hash
        return {"status": "pending", "message": "Código enviado.", "numero": numero}
    return {"status": "success", "message": "Sesión ya iniciada."}

async def verificar_codigo_async(numero, codigo, api_id, api_hash):
    session_path = f"session/{numero.replace('+', '')}.session"
    client = TelegramClient(session_path, api_id, api_hash)
    await client.connect()
    if numero not in phone_code_cache:
        return {"status": "error", "message": "Código no solicitado o ha expirado."}
    try:
        phone_code_hash = phone_code_cache.pop(numero)
        await client.sign_in(numero, code=codigo, phone_code_hash=phone_code_hash)
        return {"status": "success", "message": "Sesión iniciada correctamente."}
    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        await client.disconnect()
