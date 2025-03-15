# backend/__init__.py
from flask import Flask
from flask_cors import CORS  # Add CORS
from flask_sqlalchemy import SQLAlchemy
from config import Config

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    
    # Register routes
    from routes import init_routes
    init_routes(app)
    
    return app