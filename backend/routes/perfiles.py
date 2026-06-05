"""
routes/perfiles.py
Adaptador de entrada HTTP para perfiles.
"""

from flask import Blueprint, jsonify, request
from application.use_cases import PerfilUseCase

perfiles_bp = Blueprint('perfiles', __name__)
_use_case   = PerfilUseCase()


@perfiles_bp.route('/perfiles', methods=['GET'])
def listar_perfiles():
    perfiles = _use_case.listar_perfiles()
    return jsonify({'perfiles': perfiles, 'total': len(perfiles)}), 200


@perfiles_bp.route('/perfiles', methods=['POST'])
def crear_perfil():
    body          = request.get_json() or {}
    nombre        = body.get('nombre', '').strip()
    nombre_perfil = body.get('nombre_perfil', '').strip()
    tipo          = body.get('tipo', 'turista')

    if not nombre or not nombre_perfil:
        return jsonify({'error': 'nombre y nombre_perfil son requeridos'}), 400

    try:
        perfil = _use_case.crear_perfil(nombre, nombre_perfil, tipo)
        return jsonify({'mensaje': 'Perfil creado', 'perfil': perfil}), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400


@perfiles_bp.route('/perfiles/<string:perfil_id>', methods=['GET'])
def obtener_perfil(perfil_id):
    perfil = _use_case.obtener_perfil(perfil_id)
    if not perfil:
        return jsonify({'error': 'Perfil no encontrado'}), 404
    return jsonify(perfil), 200


@perfiles_bp.route('/perfiles/<string:perfil_id>', methods=['DELETE'])
def eliminar_perfil(perfil_id):
    try:
        nombre = _use_case.eliminar_perfil(perfil_id)
        return jsonify({'mensaje': f'Perfil "{nombre}" eliminado'}), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
