import asyncio
import os
import aiohttp
import random
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
                    print(f"Error al descargar {url}")
                    return None

    """ @staticmethod
    async def enviar_mensaje(id_celular, destinatario, messages):
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
        if not result.users:
            await client.disconnect()
            return {"status": "error", "message": "No se pudo encontrar el usuario en Telegram"}

        user = result.users[0]
        archivos_locales = []
        
        download_tasks = {}
        for idx, msg in enumerate(messages):
            tipo = msg.get("tipo")
            if tipo in ["imagen", "documento", "video", "audio"]:
                contenido = msg["content"]["body"]
                if contenido.startswith("http"):

                    download_tasks[idx] = TelegramService.descargar_archivo(contenido)
                else:
                    download_tasks[idx] = _immediate(contenido)

        download_results = {}
        if download_tasks:
            resultados = await asyncio.gather(*download_tasks.values())
            for key, value in zip(download_tasks.keys(), resultados):
                download_results[key] = value

        for idx, msg in enumerate(messages):
            tipo = msg.get("tipo")
            contenido = msg["content"]["body"]
            footer = msg["content"].get("footer", "")
            
            if tipo == "texto":
                await client.send_message(user.id, contenido)
            elif tipo in ["imagen", "documento", "video", "audio"]:
                archivo_local = download_results.get(idx)
                if archivo_local:
                    archivos_locales.append(archivo_local)
                    if tipo == "video" and "cloudflare" in contenido:
                        await client.send_file(user.id, archivo_local, caption=footer, force_document=False, supports_streaming=True)
                    else:
                        await client.send_file(user.id, archivo_local, caption=footer)

        TelegramRepository.guardar_mensaje(numero, destinatario, "Mensaje enviado", "Multimedia")
        respuesta = {"status": "success", "message": f"Mensaje enviado a {destinatario}"}

        for archivo in archivos_locales:
            if os.path.exists(archivo):
                os.remove(archivo)

        await client.disconnect()
        return respuesta """
    

    """ @staticmethod
    async def enviar_mensaje(id_celular, destinatario, messages):
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

        resultados = []
        archivos_locales = [] 
        enviados = set()

        for destinatario in destinatario:
            if destinatario in enviados:
                continue 

            try:
                contact = InputPhoneContact(client_id=0, phone=destinatario, first_name=destinatario, last_name="")
                result = await client(ImportContactsRequest([contact]))

                if not result.users:
                    resultados.append({"destinatario": destinatario, "status": "error", "message": "Usuario no encontrado"})
                    continue

                user = result.users[0]

                download_tasks = {
                    idx: TelegramService.descargar_archivo(msg["content"]["body"])
                    for idx, msg in enumerate(messages)
                    if msg.get("tipo") in ["imagen", "documento", "video", "audio"] and msg["content"]["body"].startswith("http")
                }
                download_results = await asyncio.gather(*download_tasks.values(), return_exceptions=True)
                download_results = {key: value for key, value in zip(download_tasks.keys(), download_results)}

                for idx, msg in enumerate(messages):
                    tipo = msg.get("tipo")
                    contenido = msg["content"]["body"]
                    footer = msg["content"].get("footer", "")

                    if tipo == "texto":
                        await client.send_message(user.id, contenido)
                    elif tipo in ["imagen", "documento", "video", "audio"]:
                        archivo_local = download_results.get(idx)
                        if archivo_local:
                            archivos_locales.append(archivo_local)
                            await client.send_file(user.id, archivo_local, caption=footer)

                    await asyncio.sleep(7)

                TelegramRepository.guardar_mensaje(numero, destinatario, "Mensaje enviado", "Multimedia")
                resultados.append({"destinatario": destinatario, "status": "success", "message": "Mensaje enviado"})
                enviados.add(destinatario)  # guarda el número para evitar repetirlo

            except Exception as e:
                resultados.append({"destinatario": destinatario, "status": "error", "message": str(e)})

            await asyncio.sleep(18) 

        for archivo in archivos_locales:
            if os.path.exists(archivo):
                os.remove(archivo)

        await client.disconnect()
        return resultados """
    
    @staticmethod
    async def enviar_mensaje(id_celular_list, destinatarios, messages):
        if not id_celular_list:
            return {"status": "error", "message": "Lista de id_celular vacía"}
        
        resultados = []
        archivos_locales = []
        enviados = set()
        num_disponibles = len(id_celular_list)
        
        for i, destinatario in enumerate(destinatarios):
            id_celular = id_celular_list[i % num_disponibles]  # Rotar entre los números disponibles
            credencial = TelegramRepository.obtener_credenciales(id_celular)

            if not credencial:
                resultados.append({"destinatario": destinatario, "status": "error", "message": "No se encontraron credenciales"})
                continue
            
            numero = credencial.numero
            api_id = credencial.app_id
            api_hash = credencial.api_hash
            session_path = f"session/{numero.replace('+', '')}.session"
            os.makedirs("session", exist_ok=True)
            
            client = TelegramClient(session_path, api_id, api_hash)
            await client.start(numero)
            
            try:
                contact = InputPhoneContact(client_id=0, phone=destinatario, first_name=destinatario, last_name="")
                result = await client(ImportContactsRequest([contact]))
                
                if not result.users:
                    resultados.append({"destinatario": destinatario, "status": "error", "message": "Usuario no encontrado"})
                    continue
                
                user = result.users[0]
                download_tasks = {
                    idx: TelegramService.descargar_archivo(msg["content"]["body"])
                    for idx, msg in enumerate(messages)
                    if msg.get("tipo") in ["imagen", "documento", "video", "audio"] and msg["content"]["body"].startswith("http")
                }
                download_results = await asyncio.gather(*download_tasks.values(), return_exceptions=True)
                download_results = {key: value for key, value in zip(download_tasks.keys(), download_results)}
                
                for idx, msg in enumerate(messages):
                    tipo = msg.get("tipo")
                    contenido = msg["content"]["body"]
                    footer = msg["content"].get("footer", "")
                    
                    if tipo == "texto":
                        await client.send_message(user.id, contenido)
                    elif tipo in ["imagen", "documento", "video", "audio"]:
                        archivo_local = download_results.get(idx)
                        if archivo_local:
                            archivos_locales.append(archivo_local)
                            await client.send_file(user.id, archivo_local, caption=footer)
                    
                    await asyncio.sleep(15)  # Esperar entre mensajes para evitar bloqueos
                
                TelegramRepository.guardar_mensaje(numero, destinatario, "Mensaje enviado", "Multimedia")
                resultados.append({"destinatario": destinatario, "status": "success", "message": "Mensaje enviado"})
                enviados.add(destinatario)
                
            except Exception as e:
                resultados.append({"destinatario": destinatario, "status": "error", "message": str(e)})
            
            await asyncio.sleep(30)  # Evitar demasiadas peticiones seguidas
            await client.disconnect()
        
        for archivo in archivos_locales:
            if os.path.exists(archivo):
                os.remove(archivo)
        
        return resultados
        

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

async def _immediate(result):
    return result