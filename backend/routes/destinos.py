"""
routes/destinos.py
Adaptador de entrada HTTP para destinos.
Solo maneja HTTP — la lógica está en application/use_cases.
"""

from flask import Blueprint, jsonify, request
from application.use_cases import DestinoUseCase

destinos_bp  = Blueprint('destinos', __name__)
_use_case    = DestinoUseCase()


@destinos_bp.route('/destinos', methods=['GET'])
def listar_destinos():
    categoria = request.args.get('categoria')
    destinos  = _use_case.listar_destinos(categoria)
    return jsonify({'destinos': destinos, 'total': len(destinos)}), 200


@destinos_bp.route('/destinos/<string:destino_id>', methods=['GET'])
def obtener_destino(destino_id):
    destino = _use_case.obtener_destino(destino_id)
    if not destino:
        return jsonify({'error': 'Destino no encontrado'}), 404
    return jsonify(destino), 200


@destinos_bp.route('/destinos/<string:destino_id>/visita', methods=['POST'])
def registrar_visita(destino_id):
    body      = request.get_json() or {}
    perfil_id = body.get('perfil_id')
    cantidad  = body.get('cantidad', 1)
    try:
        destino = _use_case.registrar_visita(destino_id, perfil_id, cantidad)
        return jsonify({'mensaje': 'Visita registrada', 'destino': destino}), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except OverflowError as e:
        return jsonify({'error': str(e)}), 400


@destinos_bp.route('/destinos/<string:destino_id>/salida', methods=['POST'])
def registrar_salida(destino_id):
    body     = request.get_json() or {}
    cantidad = body.get('cantidad', 1)
    try:
        destino = _use_case.registrar_salida(destino_id, cantidad)
        return jsonify({'mensaje': 'Salida registrada', 'destino': destino}), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 404


@destinos_bp.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'servicio': 'Turismo Junín API', 'db': 'Firestore'}), 200
