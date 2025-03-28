import os
import requests
import aiohttp
from telethon import TelegramClient
from telethon.tl.functions.contacts import ImportContactsRequest
from telethon.tl.types import InputPhoneContact
from modules.Tme.domain.TelegramRepository import TelegramRepository

phone_code_cache = {}

class TelegramService:
    @staticmethod
    async def descargar_archivo(url):
        nombre_archivo = url.split("/")[-1]
        ruta_archivo = os.path.join("temp", nombre_archivo)

        os.makedirs("temp", exist_ok=True)

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    with open(ruta_archivo, "wb") as f:
                        f.write(await response.read())
                    return ruta_archivo
                else:
                    print(f" Error al descargar {url}")
                    return None

    @staticmethod
    async def enviar_mensaje(id_celular, destinatario, mensaje, titulo, archivo_urls=None):
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

            archivos_locales = []
            if archivo_urls:
                for archivo_url in archivo_urls:
                    if archivo_url.startswith("http"):
                        archivo_local = await TelegramService.descargar_archivo(archivo_url)
                        if archivo_local:
                            archivos_locales.append(archivo_local)
                    else:
                        archivos_locales.append(archivo_url)

                await client.send_file(user.id, archivos_locales, caption=mensaje)

                for archivo in archivos_locales:
                    if os.path.exists(archivo):
                        os.remove(archivo)

            else:
                await client.send_message(user.id, mensaje)

            TelegramRepository.guardar_mensaje(numero, destinatario, mensaje, titulo)
            await client.disconnect()
            return {"status": "success", "message": f"Mensaje enviado a {destinatario}"}
        else:
            await client.disconnect()
            return {"status": "error", "message": "No se pudo encontrar el usuario en Telegram"}
