from flask import Flask
from shared.database.Database import init_db
from modules.Tme.infrastructure.Telegram_Routes import bp as telegram_bp

def create_app():
    app = Flask(__name__)
    init_db(app)
    app.register_blueprint(telegram_bp)
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
