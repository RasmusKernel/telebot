from flask import Flask
from shared.database.Database import init_db
from modules.Tme.infrastructure.TelegramRoutes import telegram_bp
import threading
from modules.RabbitMQ.infrastructure.RabbitMQConsumer import RabbitMQConsumer


def start_rabbitmq_consumer(app):
    consumer = RabbitMQConsumer(queue_name="telegram_queue", app = app)
    consumer.start_consuming()

def create_app():
    app = Flask(__name__)
    init_db(app)
    app.register_blueprint(telegram_bp, url_prefix="/api/telegram")
    consumer_thread = threading.Thread(target=start_rabbitmq_consumer, args=(app,) , daemon=True)
    consumer_thread.start()

    return app
