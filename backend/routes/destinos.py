"""
routes/destinos.py
Endpoints para gestión de destinos turísticos — Firestore
"""

from flask import Blueprint, jsonify, request
from datetime import datetime, timezone
from config.firebase_init import get_db

destinos_bp = Blueprint('destinos', __name__)


def _porcentaje(visitantes, capacidad):
    if capacidad == 0:
        return 0
    return round((visitantes / capacidad) * 100, 1)


def _estado(pct):
    if pct >= 90:
        return 'critico'
    elif pct >= 70:
        return 'alto'
    elif pct >= 40:
        return 'moderado'
    return 'bajo'


def _destino_to_dict(doc_id, data):
    visitantes = data.get('visitantes_actuales', 0)
    capacidad  = data.get('capacidad_max', 1)
    pct        = _porcentaje(visitantes, capacidad)
    return {
        'id':                   doc_id,
        'nombre':               data.get('nombre'),
        'ubicacion':            data.get('ubicacion'),
        'descripcion':          data.get('descripcion'),
        'categoria':            data.get('categoria'),
        'capacidad_max':        capacidad,
        'visitantes_actuales':  visitantes,
        'porcentaje_ocupacion': pct,
        'estado':               _estado(pct),
        'latitud':              data.get('latitud'),
        'longitud':             data.get('longitud'),
    }


# ── GET /destinos ─────────────────────────────────────────────
@destinos_bp.route('/destinos', methods=['GET'])
def listar_destinos():
    db = get_db()
    categoria = request.args.get('categoria')

    query = db.collection('destinos')
    if categoria:
        query = query.where('categoria', '==', categoria)

    docs = query.stream()
    destinos = [_destino_to_dict(d.id, d.to_dict()) for d in docs]
    destinos.sort(key=lambda x: x['nombre'])

    return jsonify({'destinos': destinos, 'total': len(destinos)}), 200


# ── GET /destinos/:id ──────────────────────────────────────────
@destinos_bp.route('/destinos/<string:destino_id>', methods=['GET'])
def obtener_destino(destino_id):
    db  = get_db()
    doc = db.collection('destinos').document(destino_id).get()

    if not doc.exists:
        return jsonify({'error': 'Destino no encontrado'}), 404

    return jsonify(_destino_to_dict(doc.id, doc.to_dict())), 200


# ── POST /destinos/:id/visita ──────────────────────────────────
@destinos_bp.route('/destinos/<string:destino_id>/visita', methods=['POST'])
def registrar_visita(destino_id):
    db      = get_db()
    ref     = db.collection('destinos').document(destino_id)
    doc     = ref.get()

    if not doc.exists:
        return jsonify({'error': 'Destino no encontrado'}), 404

    data     = doc.to_dict()
    body     = request.get_json() or {}
    cantidad = body.get('cantidad', 1)
    perfil_id = body.get('perfil_id')

    visitantes = data.get('visitantes_actuales', 0)
    capacidad  = data.get('capacidad_max', 0)

    if visitantes + cantidad > capacidad:
        return jsonify({
            'error': 'Capacidad máxima alcanzada',
            'capacidad_max': capacidad,
            'visitantes_actuales': visitantes
        }), 400

    # Actualizar contador
    nuevos_visitantes = visitantes + cantidad
    ref.update({'visitantes_actuales': nuevos_visitantes})

    # Registrar visita
    db.collection('visitas').add({
        'destino_id': destino_id,
        'perfil_id':  perfil_id,
        'cantidad':   cantidad,
        'fecha':      datetime.now(timezone.utc).isoformat(),
    })

    # Generar alerta si es necesario
    data['visitantes_actuales'] = nuevos_visitantes
    _generar_alerta_si_necesario(db, destino_id, data)

    destino_actualizado = ref.get()
    return jsonify({
        'mensaje': 'Visita registrada',
        'destino': _destino_to_dict(destino_id, destino_actualizado.to_dict())
    }), 200


# ── POST /destinos/:id/salida ──────────────────────────────────
@destinos_bp.route('/destinos/<string:destino_id>/salida', methods=['POST'])
def registrar_salida(destino_id):
    db  = get_db()
    ref = db.collection('destinos').document(destino_id)
    doc = ref.get()

    if not doc.exists:
        return jsonify({'error': 'Destino no encontrado'}), 404

    data     = doc.to_dict()
    body     = request.get_json() or {}
    cantidad = body.get('cantidad', 1)

    nuevos = max(0, data.get('visitantes_actuales', 0) - cantidad)
    ref.update({'visitantes_actuales': nuevos})

    destino_actualizado = ref.get()
    return jsonify({
        'mensaje': 'Salida registrada',
        'destino': _destino_to_dict(destino_id, destino_actualizado.to_dict())
    }), 200


# ── GET /health ────────────────────────────────────────────────
@destinos_bp.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'servicio': 'Turismo Junín API', 'db': 'Firestore'}), 200


# ── Función auxiliar ───────────────────────────────────────────
def _generar_alerta_si_necesario(db, destino_id, data):
    visitantes = data.get('visitantes_actuales', 0)
    capacidad  = data.get('capacidad_max', 1)
    nombre     = data.get('nombre', '')
    pct        = _porcentaje(visitantes, capacidad)

    tipo = None
    if pct >= 90:
        tipo = 'critica'
    elif pct >= 70:
        tipo = 'advertencia'

    if not tipo:
        return

    # Verificar si ya existe alerta activa del mismo tipo
    existentes = (
        db.collection('alertas')
        .where('destino_id', '==', destino_id)
        .where('tipo', '==', tipo)
        .where('activa', '==', True)
        .limit(1)
        .stream()
    )

    if list(existentes):
        return  # Ya existe, no duplicar

    if tipo == 'critica':
        mensaje = f"{nombre} ha alcanzado el {pct}% de su capacidad. Acceso restringido recomendado."
    else:
        mensaje = f"{nombre} está al {pct}% de su capacidad. Se recomienda visitar destinos alternativos."

    db.collection('alertas').add({
        'destino_id': destino_id,
        'destino':    nombre,
        'tipo':       tipo,
        'mensaje':    mensaje,
        'activa':     True,
        'fecha':      datetime.now(timezone.utc).isoformat(),
    })
