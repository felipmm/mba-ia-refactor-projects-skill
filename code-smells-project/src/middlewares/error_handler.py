import logging
from flask import jsonify

logger = logging.getLogger(__name__)


def register_error_handlers(app):

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"erro": "Recurso não encontrado"}), 404

    @app.errorhandler(405)
    def method_not_allowed(e):
        return jsonify({"erro": "Método não permitido"}), 405

    @app.errorhandler(500)
    def internal_error(e):
        logger.exception("Erro interno não tratado: %s", e)
        return jsonify({"erro": "Erro interno do servidor"}), 500
