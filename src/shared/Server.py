from flask import Flask
from src.shared.database.Database import init_db
from src.modules.Tme.infrastructure.TelegramRoutes import telegram_bp

def create_app():
    app = Flask(__name__)
    init_db(app)
    app.register_blueprint(telegram_bp, url_prefix="/api/telegram")
    return app
