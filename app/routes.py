from flask import Blueprint, request, jsonify, Flask
import asyncio
import os
from telethon.tl.types import InputPhoneContact
from telethon import TelegramClient
from .telegram import enviar_mensaje, obtener_credenciales
from .database import db
from .models import Celular
import asyncio

bp = Blueprint("routes", __name__)

SESSION_DIR = "session"
os.makedirs(SESSION_DIR, exist_ok=True)
session = {}

phone_code_cache = {}

@bp.route('/enviar_mensaje', methods=['POST'])
def api_enviar_mensaje():
    data = request.json
    if not all(k in data for k in ("id_celular", "destinatario", "mensaje", "titulo")):
        return jsonify({"status": "error", "message": "Todos los parámetros son obligatorios"}), 400
    archivo_url = data.get("archivo_url", None)
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    resultado = loop.run_until_complete(enviar_mensaje(
        data["id_celular"],
        data["destinatario"],
        data["mensaje"],
        data["titulo"],
        archivo_url
    ))
    return jsonify(resultado)

@bp.route('/guardar_numero', methods=['POST'])
def api_guardar_numero():
    data = request.json
    if not all(k in data for k in ("numero", "app_id", "api_hash", "nombre")):
        return jsonify({"status": "error", "message": "Faltan datos en la solicitud"}), 400

    nuevo_numero = Celular.query.filter_by(numero=data["numero"]).first()
    if nuevo_numero:
        nuevo_numero.app_id = data["app_id"]
        nuevo_numero.api_hash = data["api_hash"]
        nuevo_numero.nombre = data["nombre"]
    else:
        nuevo_numero = Celular(numero=data["numero"], app_id=data["app_id"], api_hash=data["api_hash"], nombre=data["nombre"])
        db.session.add(nuevo_numero)

    db.session.commit()
    return jsonify({"status": "success", "message": f"Número {data['numero']} guardado correctamente."}), 201

@bp.route('/listar_numeros', methods=['GET'])
def api_listar_numeros():
    numeros = Celular.query.with_entities(Celular.id, Celular.numero, Celular.nombre).all()
    return jsonify({"status": "success", "data": [{"id": n.id, "numero": n.numero, "nombre": n.nombre} for n in numeros]})


async def send_code(client, numero):
    await client.connect()
    phone_code_hash = await client.send_code_request(numero)
    return phone_code_hash

async def iniciar_sesion_async(numero, api_id, api_hash):
    session_path = f"session/{numero.replace('+', '')}.session"
    os.makedirs("session", exist_ok=True)
    client = TelegramClient(session_path, api_id, api_hash)
    await client.connect()
    if not await client.is_user_authorized():
        code_request = await client.send_code_request(numero)
        phone_code_cache[numero] = code_request.phone_code_hash  # Guardar el hash temporalmente
        return {"status": "pending", "message": "Código enviado.", "numero": numero}
    return {"status": "success", "message": "Sesión ya iniciada."}

async def verificar_codigo_async(numero, codigo, api_id, api_hash):
    session_path = f"session/{numero.replace('+', '')}.session"
    client = TelegramClient(session_path, api_id, api_hash)
    await client.connect()
    if numero not in phone_code_cache:
        return {"status": "error", "message": "Código no solicitado o ha expirado."}
    try:
        phone_code_hash = phone_code_cache.pop(numero)  # Recuperar y eliminar el hash almacenado
        await client.sign_in(numero, code=codigo, phone_code_hash=phone_code_hash)
        return {"status": "success", "message": "Sesión iniciada correctamente."}
    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        await client.disconnect()

@bp.route('/v1/codigo', methods=['POST'])
def iniciar_sesion():
    data = request.json
    id_celular = data.get("id_celular")
    celular = Celular.query.get(id_celular)
    if not celular:
        return jsonify({"status": "error", "message": "Celular no encontrado"}), 400
    numero = celular.numero
    api_id = celular.app_id
    api_hash = celular.api_hash
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    resultado = loop.run_until_complete(iniciar_sesion_async(numero, api_id, api_hash))
    
    return jsonify(resultado)

@bp.route('/v1/verificarcode', methods=['POST'])
def verificar_codigo():
    data = request.json
    id_celular = data.get("id_celular")
    codigo = data.get("codigo")
    celular = Celular.query.get(id_celular)
    if not celular:
        return jsonify({"status": "error", "message": "Celular no encontrado"}), 400
    numero = celular.numero
    api_id = celular.app_id
    api_hash = celular.api_hash
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    resultado = loop.run_until_complete(verificar_codigo_async(numero, codigo, api_id, api_hash))
    return jsonify(resultado)