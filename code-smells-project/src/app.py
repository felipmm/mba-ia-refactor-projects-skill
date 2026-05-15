import logging
from flask import Flask
from flask_cors import CORS
from config.settings import Config
from database import close_db, init_db
from views.routes import register_routes
from middlewares.error_handler import register_error_handlers

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app)
    app.teardown_appcontext(close_db)
    init_db(app)
    register_routes(app)
    register_error_handlers(app)
    return app


if __name__ == "__main__":
    app = create_app()
    print("=" * 50)
    print("SERVIDOR INICIADO")
    print("Rodando em http://localhost:5000")
    print("=" * 50)
    app.run(host="0.0.0.0", port=5000)
