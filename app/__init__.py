import os
from flask import Flask, send_from_directory, make_response
from .config import Config
from .extensions import db, migrate


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)

    from .models import relatorio  # noqa: F401
    from .blueprints.web import web_bp
    from .blueprints.api import api_bp

    app.register_blueprint(web_bp)
    app.register_blueprint(api_bp, url_prefix="/api")

    with app.app_context():
        try:
            db.create_all()
        except Exception as exc:
            app.logger.warning(f"Aviso ao inicializar tabelas no banco: {exc}")

    @app.route("/manifest.json")
    def manifest():
        return send_from_directory(
            os.path.join(app.root_path, "static"),
            "manifest.json",
            mimetype="application/manifest+json",
        )

    @app.route("/sw.js")
    def service_worker():
        response = make_response(
            send_from_directory(
                os.path.join(app.root_path, "static"),
                "sw.js",
                mimetype="application/javascript",
            )
        )
        response.headers["Service-Worker-Allowed"] = "/"
        response.headers["Cache-Control"] = "no-cache"
        return response

    return app
