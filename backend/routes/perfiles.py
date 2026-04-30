"""
routes/perfiles.py
Endpoints para gestión de perfiles de usuario — Firestore
"""

from flask import Blueprint, jsonify, request
from datetime import datetime, timezone
from config.firebase_init import get_db

perfiles_bp = Blueprint('perfiles', __name__)


def _perfil_to_dict(doc_id, data, total_visitas=0):
    return {
        'id':             doc_id,
        'nombre':         data.get('nombre'),
        'nombre_perfil':  data.get('nombre_perfil'),
        'tipo':           data.get('tipo', 'turista'),
        'total_visitas':  total_visitas,
        'fecha_creacion': data.get('fecha_creacion'),
    }


def _contar_visitas(db, perfil_id):
    visitas = db.collection('visitas').where('perfil_id', '==', perfil_id).stream()
    return sum(1 for _ in visitas)


# ── GET /perfiles ──────────────────────────────────────────────
@perfiles_bp.route('/perfiles', methods=['GET'])
def listar_perfiles():
    db   = get_db()
    docs = db.collection('perfiles').stream()
    perfiles = []
    for d in docs:
        data = d.to_dict()
        total = _contar_visitas(db, d.id)
        perfiles.append(_perfil_to_dict(d.id, data, total))
    perfiles.sort(key=lambda x: x['nombre_perfil'])
    return jsonify({'perfiles': perfiles, 'total': len(perfiles)}), 200


# ── POST /perfiles ─────────────────────────────────────────────
@perfiles_bp.route('/perfiles', methods=['POST'])
def crear_perfil():
    db   = get_db()
    body = request.get_json() or {}

    nombre        = body.get('nombre', '').strip()
    nombre_perfil = body.get('nombre_perfil', '').strip()

    if not nombre or not nombre_perfil:
        return jsonify({'error': 'nombre y nombre_perfil son requeridos'}), 400

    # Verificar unicidad
    existentes = (
        db.collection('perfiles')
        .where('nombre_perfil', '==', nombre_perfil)
        .limit(1)
        .stream()
    )
    if list(existentes):
        return jsonify({'error': 'El nombre de perfil ya existe'}), 400

    nuevo = {
        'nombre':         nombre,
        'nombre_perfil':  nombre_perfil,
        'tipo':           body.get('tipo', 'turista'),
        'fecha_creacion': datetime.now(timezone.utc).isoformat(),
    }
    _, ref = db.collection('perfiles').add(nuevo)

    return jsonify({
        'mensaje': 'Perfil creado',
        'perfil':  _perfil_to_dict(ref.id, nuevo, 0)
    }), 201


# ── GET /perfiles/:id ──────────────────────────────────────────
@perfiles_bp.route('/perfiles/<string:perfil_id>', methods=['GET'])
def obtener_perfil(perfil_id):
    db  = get_db()
    doc = db.collection('perfiles').document(perfil_id).get()

    if not doc.exists:
        return jsonify({'error': 'Perfil no encontrado'}), 404

    total = _contar_visitas(db, perfil_id)
    return jsonify(_perfil_to_dict(doc.id, doc.to_dict(), total)), 200


# ── DELETE /perfiles/:id ───────────────────────────────────────
@perfiles_bp.route('/perfiles/<string:perfil_id>', methods=['DELETE'])
def eliminar_perfil(perfil_id):
    db  = get_db()
    ref = db.collection('perfiles').document(perfil_id)
    doc = ref.get()

    if not doc.exists:
        return jsonify({'error': 'Perfil no encontrado'}), 404

    nombre_perfil = doc.to_dict().get('nombre_perfil', '')
    ref.delete()

    return jsonify({'mensaje': f'Perfil "{nombre_perfil}" eliminado'}), 200
