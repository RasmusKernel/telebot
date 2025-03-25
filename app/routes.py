from flask import Blueprint, request, jsonify
import asyncio
from .telegram import enviar_mensaje, obtener_credenciales
from .database import db
from .models import Celular

bp = Blueprint("routes", __name__)

@bp.route('/enviar_mensaje', methods=['POST'])
def api_enviar_mensaje():
    data = request.json
    if not all(k in data for k in ("id_celular", "destinatario", "mensaje", "titulo")):
        return jsonify({"status": "error", "message": "Todos los parámetros son obligatorios"}), 400

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    resultado = loop.run_until_complete(enviar_mensaje(data["id_celular"], data["destinatario"], data["mensaje"], data["titulo"]))

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