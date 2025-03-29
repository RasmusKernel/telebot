import pika
import json
import asyncio
from shared.Config import RABBITMQ_HOST, RABBITMQ_PORT, RABBITMQ_USER, RABBITMQ_PASSWORD
from modules.Tme.application.TelegramService import TelegramService

class RabbitMQConsumer:
    def __init__(self, queue_name="telegram_queue", app=None):
        self.queue_name = queue_name
        self.app = app
        credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASSWORD)

        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=RABBITMQ_HOST,
                port=RABBITMQ_PORT,
                credentials=credentials
            )
        )
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=self.queue_name, durable=True)
        self.channel.basic_qos(prefetch_count=1)

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

            if self.app:
                with self.app.app_context():
                    resultado = asyncio.run(
                        TelegramService.enviar_mensaje(id_celular, destinatario, messages)
                    )
            else:
                resultado = asyncio.run(
                    TelegramService.enviar_mensaje(id_celular, destinatario, messages)
                )

            print(f"Mensaje procesado con éxito: {resultado}")
            ch.basic_ack(delivery_tag=method.delivery_tag)

        except json.JSONDecodeError:
            print("Error: No se pudo decodificar el JSON.")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

        except Exception as e:
            print(f"Error al procesar mensaje: {str(e)}")
            print(f"Contenido del mensaje fallido: {body}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

    def start_consuming(self):
        print(f"Esperando mensajes en la cola '{self.queue_name}'...")
        self.channel.basic_consume(queue=self.queue_name, on_message_callback=self.callback)
        self.channel.start_consuming()

if __name__ == "__main__":
    consumer = RabbitMQConsumer()
    consumer.start_consuming()
