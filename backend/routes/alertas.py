"""
routes/alertas.py
Adaptador de entrada HTTP para alertas.
"""

from flask import Blueprint, jsonify
from application.use_cases import AlertaUseCase

alertas_bp = Blueprint('alertas', __name__)
_use_case  = AlertaUseCase()


@alertas_bp.route('/alertas', methods=['GET'])
def listar_alertas():
    alertas = _use_case.listar_alertas_activas()
    return jsonify({'alertas': alertas, 'total': len(alertas)}), 200


@alertas_bp.route('/alertas/<string:alerta_id>', methods=['DELETE'])
def desactivar_alerta(alerta_id):
    try:
        _use_case.resolver_alerta(alerta_id)
        return jsonify({'mensaje': 'Alerta desactivada'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 404
