from flask import Flask
from app.config.settings import Config, TestingConfig
from app.infrastructure.database.db import db
from app.presentation.routes.auth_routes import auth_bp
from app.presentation.routes.order_routes import order_bp


def create_app(config_name="default"):
    app = Flask(__name__)
    if config_name == "testing":
        app.config.from_object(TestingConfig)
    else:
        app.config.from_object(Config)

    db.init_app(app)

    from app.infrastructure.database.models import User, Order, OrderItem

    app.register_blueprint(auth_bp)
    app.register_blueprint(order_bp)

    return app
