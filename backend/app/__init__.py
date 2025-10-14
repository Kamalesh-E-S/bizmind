from flask import Flask
from flask_cors import CORS
from .config import Config
from .database import init_db
from .endpoints import register_blueprints

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app)
    with app.app_context():
        init_db()
    register_blueprints(app)
    return app
