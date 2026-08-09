from __future__ import annotations

from flask import Flask, jsonify

from api.routes.budgets import budgetsBlueprint
from api.routes.pricing import pricingBlueprint
from core.database.connection import Base, engine


def createApp() -> Flask:
    app = Flask(__name__)
    Base.metadata.create_all(bind=engine)

    app.register_blueprint(budgetsBlueprint)
    app.register_blueprint(pricingBlueprint)

    @app.get("/health")
    def healthcheck():
        return jsonify({"status": "ok"})

    @app.errorhandler(Exception)
    def handleException(error: Exception):
        statusCode = getattr(error, "code", 500)
        return jsonify({"error": str(error), "status_code": statusCode}), statusCode

    return app


app = createApp()


if __name__ == "__main__":
    app.run(debug=True)
