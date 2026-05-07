"""
error_handlers.py
Manejadores de error globales
"""

from flask import jsonify


def register_error_handlers(app):

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({'error': 'Endpoint no encontrado'}), 404

    @app.errorhandler(405)
    def method_not_allowed(e):
        return jsonify({'error': 'Método no permitido'}), 405

    @app.errorhandler(500)
    def internal_error(e):
        return jsonify({'error': 'Error interno del servidor'}), 500
