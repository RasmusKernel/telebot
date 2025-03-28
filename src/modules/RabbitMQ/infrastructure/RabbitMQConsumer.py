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
        mensaje = json.loads(body)
        print(f" Mensaje recibido en la cola: {mensaje}")
        
        archivo_urls = mensaje.get("archivo_urls", [])
        if not isinstance(archivo_urls, list):
            archivo_urls = [archivo_urls]

        try:
            if self.app:
                with self.app.app_context():
                    resultado = asyncio.run(
                        TelegramService.enviar_mensaje(
                            mensaje["id_celular"],
                            mensaje["destinatario"],
                            mensaje["mensaje"],
                            mensaje["titulo"],
                            archivo_urls
                        )
                    )
            else:
                resultado = asyncio.run(
                    TelegramService.enviar_mensaje(
                        mensaje["id_celular"],
                        mensaje["destinatario"],
                        mensaje["mensaje"],
                        mensaje["titulo"],
                        archivo_urls
                    )
                )
            print(f" Resultado del envío: {resultado}")
            ch.basic_ack(delivery_tag=method.delivery_tag)

        except Exception as e:
            print(f" Error al enviar mensaje: {str(e)}")
            ch.basic_ack(delivery_tag=method.delivery_tag)

    def start_consuming(self):
        print(f" Consumidor iniciado, esperando mensajes en la cola '{self.queue_name}'...")
        self.channel.basic_consume(queue=self.queue_name, on_message_callback=self.callback)
        self.channel.start_consuming()

if __name__ == "__main__":
    consumer = RabbitMQConsumer()
    consumer.start_consuming()
