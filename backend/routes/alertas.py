"""
routes/alertas.py
Endpoints para consulta de alertas de capacidad — Firestore
"""

from flask import Blueprint, jsonify
from config.firebase_init import get_db

alertas_bp = Blueprint('alertas', __name__)


# ── GET /alertas ───────────────────────────────────────────────
@alertas_bp.route('/alertas', methods=['GET'])
def listar_alertas():
    db = get_db()
    docs = (
        db.collection('alertas')
        .where('activa', '==', True)
        .stream()
    )
    alertas = [{'id': d.id, **d.to_dict()} for d in docs]
    alertas.sort(key=lambda x: x.get('fecha', ''), reverse=True)

    return jsonify({'alertas': alertas, 'total': len(alertas)}), 200


# ── DELETE /alertas/:id ────────────────────────────────────────
@alertas_bp.route('/alertas/<string:alerta_id>', methods=['DELETE'])
def desactivar_alerta(alerta_id):
    db  = get_db()
    ref = db.collection('alertas').document(alerta_id)
    doc = ref.get()

    if not doc.exists:
        return jsonify({'error': 'Alerta no encontrada'}), 404

    ref.update({'activa': False})
    return jsonify({'mensaje': 'Alerta desactivada'}), 200
