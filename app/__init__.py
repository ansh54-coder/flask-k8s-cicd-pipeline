from flask import Flask
from prometheus_flask_exporter import PrometheusMetrics

from app.config import Config
from app.extensions import db, jwt, migrate
from app.routes.health import health_bp
from app.routes.products import products_bp
from app.routes.orders import orders_bp
from app.routes.users import users_bp


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    PrometheusMetrics(
        app,
        path="/metrics",
        export_defaults=True,
    )

    app.register_blueprint(health_bp)
    app.register_blueprint(products_bp, url_prefix="/api/v1/products")
    app.register_blueprint(orders_bp, url_prefix="/api/v1/orders")
    app.register_blueprint(users_bp, url_prefix="/api/v1/users")

    register_error_handlers(app)

    return app


def register_error_handlers(app):
    from app.utils.errors import APIError

    @app.errorhandler(APIError)
    def handle_api_error(error):
        return {
            "error": error.message,
            "status": error.status_code,
        }, error.status_code

    @app.errorhandler(404)
    def handle_not_found(_):
        return {
            "error": "Resource not found",
            "status": 404,
        }, 404

    @app.errorhandler(405)
    def handle_method_not_allowed(_):
        return {
            "error": "Method not allowed",
            "status": 405,
        }, 405

    @app.errorhandler(500)
    def handle_internal_error(error):
        app.logger.exception("Unhandled exception: %s", error)
        return {
            "error": "Internal server error",
            "status": 500,
        }, 500
