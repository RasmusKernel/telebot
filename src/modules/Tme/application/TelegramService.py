import os
import requests
from telethon import TelegramClient
from telethon.tl.functions.contacts import ImportContactsRequest
from telethon.tl.types import InputPhoneContact
from src.modules.Tme.domain.TelegramRepository import TelegramRepository

phone_code_cache = {}

class TelegramService:
    @staticmethod
    async def enviar_mensaje(id_celular, destinatario, mensaje, titulo, archivo_url=None):
        credencial = TelegramRepository.obtener_credenciales(id_celular)
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
            if archivo_url:
                archivo_local = archivo_url.split("/")[-1]
                response = requests.get(archivo_url)
                if response.status_code == 200:
                    with open(archivo_local, "wb") as f:
                        f.write(response.content)
                    await client.send_file(user.id, archivo_local, caption=mensaje)
                    os.remove(archivo_local)
                else:
                    return {"status": "error", "message": "No se pudo descargar el archivo"}
            else:
                await client.send_message(user.id, mensaje)

            TelegramRepository.guardar_mensaje(numero, destinatario, mensaje, titulo)
            await client.disconnect()
            return {"status": "success", "message": f"Mensaje enviado a {destinatario}"}
        else:
            await client.disconnect()
            return {"status": "error", "message": "No se pudo encontrar el usuario en Telegram"}

    @staticmethod
    async def iniciar_sesion_async(numero, api_id, api_hash):
        session_path = f"session/{numero.replace('+', '')}.session"
        os.makedirs("session", exist_ok=True)
        client = TelegramClient(session_path, api_id, api_hash)
        await client.connect()

        if not await client.is_user_authorized():
            code_request = await client.send_code_request(numero)
            phone_code_cache[numero] = code_request.phone_code_hash
            return {"status": "pending", "message": "Código enviado.", "numero": numero, "phone_code_hash": code_request.phone_code_hash}

        return {"status": "success", "message": "Sesión ya iniciada."}

    @staticmethod
    async def verificar_codigo_async(numero, codigo, api_id, api_hash):
        session_path = f"session/{numero.replace('+', '')}.session"
        client = TelegramClient(session_path, api_id, api_hash)
        await client.connect()

        if numero not in phone_code_cache:
            return {"status": "error", "message": "Código no solicitado o ha expirado."}
        
        phone_code_hash = phone_code_cache.pop(numero)

        try:
            await client.sign_in(numero, codigo, phone_code_hash=phone_code_hash)
            return {"status": "success", "message": "Sesión iniciada correctamente."}
        except Exception as e:
            return {"status": "error", "message": str(e)}
        finally:
            await client.disconnect()
