from flask import Blueprint, request, jsonify
import asyncio
from modules.Tme.application.TelegramService import TelegramService
from modules.Tme.domain.TelegramRepository import TelegramRepository
from modules.Tme.domain.Telegram import Celular
from shared.database.Database import db

telegram_bp = Blueprint("telegram", __name__)

@telegram_bp.route('/v1/enviar_mensaje', methods=['POST'])
def api_enviar_mensaje():
    data = request.json
    if not all(k in data for k in ("id_celular", "destinatario", "mensaje", "titulo")):
        return jsonify({"status": "error", "message": "Todos los parámetros son obligatorios"}), 400

    archivo_url = data.get("archivo_url", None)
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    resultado = loop.run_until_complete(
        TelegramService.enviar_mensaje(data["id_celular"], data["destinatario"], data["mensaje"], data["titulo"], archivo_url)
    )
    return jsonify(resultado)

@telegram_bp.route('/v1/guardar_numero', methods=['POST'])
def api_guardar_numero():
    data = request.json
    if not all(k in data for k in ("numero", "app_id", "api_hash", "nombre")):
        return jsonify({"status": "error", "message": "Faltan datos en la solicitud"}), 400

    celular = Celular.query.filter_by(numero=data["numero"]).first()
    if celular:
        celular.app_id = data["app_id"]
        celular.api_hash = data["api_hash"]
        celular.nombre = data["nombre"]
    else:
        celular = Celular(numero=data["numero"], app_id=data["app_id"], api_hash=data["api_hash"], nombre=data["nombre"])
        db.session.add(celular)

    db.session.commit()
    return jsonify({"status": "success", "message": f"Número {data['numero']} guardado correctamente."}), 201

@telegram_bp.route('/v1/listar_numeros', methods=['GET'])
def api_listar_numeros():
    numeros = Celular.query.with_entities(Celular.id, Celular.numero, Celular.nombre).all()
    return jsonify({
        "status": "success",
        "data": [{"id": n.id, "numero": n.numero, "nombre": n.nombre} for n in numeros]
    })

@telegram_bp.route('/v1/codigo', methods=['POST'])
def iniciar_sesion():
    data = request.json
    id_celular = data.get("id_celular")
    celular = Celular.query.get(id_celular)
    if not celular:
        return jsonify({"status": "error", "message": "Celular no encontrado"}), 400

    resultado = asyncio.run(TelegramService.iniciar_sesion_async(celular.numero, celular.app_id, celular.api_hash))
    return jsonify(resultado)

@telegram_bp.route('/v1/verificarcode', methods=['POST'])
def verificar_codigo():
    data = request.json
    id_celular = data.get("id_celular")
    codigo = data.get("codigo")
    celular = Celular.query.get(id_celular)
    if not celular:
        return jsonify({"status": "error", "message": "Celular no encontrado"}), 400

    resultado = asyncio.run(TelegramService.verificar_codigo_async(celular.numero, codigo, celular.app_id, celular.api_hash))
    return jsonify(resultado)
