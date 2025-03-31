import pika
import json
import asyncio
import time
from shared.Config import RABBITMQ_HOST, RABBITMQ_PORT, RABBITMQ_USER, RABBITMQ_PASSWORD
from modules.Tme.application.TelegramService import TelegramService

class RabbitMQConsumer:
    def __init__(self, queue_name="telegram_queue", app=None):
        self.queue_name = queue_name
        self.app = app
        self.processed_messages = set()
        self.reconnect_delay = 7
        self.connect()

    def connect(self):
        """Conecta a RabbitMQ y declara la cola con reconexión automática."""
        credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASSWORD)
        while True:
            try:
                self.connection = pika.BlockingConnection(
                    pika.ConnectionParameters(
                        host=RABBITMQ_HOST,
                        port=RABBITMQ_PORT,
                        credentials=credentials,
                        heartbeat=600  # Mantiene la conexión activa
                    )
                )
                self.channel = self.connection.channel()
                self.channel.queue_declare(queue=self.queue_name, durable=True)
                self.channel.basic_qos(prefetch_count=1)
                print(f"Conectado a RabbitMQ en la cola '{self.queue_name}'")
                break
            except pika.exceptions.AMQPConnectionError:
                print("Fallo al conectar a RabbitMQ. Reintentando en 5 segundos...")
                time.sleep(self.reconnect_delay)

    def callback(self, ch, method, properties, body):
        try:
            if isinstance(body, bytes):
                body = body.decode("utf-8")

            mensaje = json.loads(body)
            if isinstance(mensaje, str):  
                mensaje = json.loads(mensaje)

            if not isinstance(mensaje, dict):
                raise ValueError("El mensaje recibido no tiene el formato esperado.")

            print(f"Mensaje recibido: {mensaje}")

            id_celular = mensaje.get("id_celular")
            destinatario = mensaje.get("destinatario")
            messages = mensaje.get("messages", [])

            if not id_celular or not destinatario or not messages:
                raise ValueError("El mensaje recibido no tiene todos los campos requeridos.")
            mensaje_id = f"{id_celular}-{destinatario}-{hash(json.dumps(messages))}"
            if mensaje_id in self.processed_messages:
                print(f"Mensaje ya procesado, ignorando: {mensaje_id}")
                ch.basic_ack(delivery_tag=method.delivery_tag)
                return
            self.processed_messages.add(mensaje_id)
            if self.app:
                with self.app.app_context():
                    resultado = asyncio.run(self.enviar_mensaje_async(id_celular, destinatario, messages))
            else:
                resultado = asyncio.run(self.enviar_mensaje_async(id_celular, destinatario, messages))

            print(f"Mensaje procesado con éxito: {resultado}")
            time.sleep(10)  # Evita sobrecarga en la API de Telegram
            ch.basic_ack(delivery_tag=method.delivery_tag)

        except json.JSONDecodeError:
            print("Error: No se pudo decodificar el JSON.")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

        except Exception as e:
            print(f"Error al procesar mensaje: {str(e)}")
            print(f"Contenido del mensaje fallido: {body}")
            time.sleep(10)  # Espera antes de reenviar
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

    async def enviar_mensaje_async(self, id_celular, destinatario, messages):
        """Ejecuta la función de envío de mensajes de TelegramService de manera asíncrona."""
        return await TelegramService.enviar_mensaje(id_celular, destinatario, messages)

    def start_consuming(self):
        print(f"Esperando mensajes en la cola '{self.queue_name}'...")
        while True:
            try:
                self.channel.basic_consume(queue=self.queue_name, on_message_callback=self.callback)
                self.channel.start_consuming()
            except (pika.exceptions.AMQPConnectionError, pika.exceptions.StreamLostError):
                print("Conexión con RabbitMQ perdida, intentando reconectar...")
                time.sleep(self.reconnect_delay)
                self.connect()
            except Exception as e:
                print(f"Error inesperado: {e}, reintentando en {self.reconnect_delay} segundos...")
                time.sleep(self.reconnect_delay)
                self.connect()

if __name__ == "__main__":
    consumer = RabbitMQConsumer()
    consumer.start_consuming()
