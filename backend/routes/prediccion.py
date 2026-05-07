"""
routes/prediccion.py
Endpoints para el predictor de afluencia ML
"""

from flask import Blueprint, jsonify, request
from datetime import datetime
from services.predictor_ml import predecir_afluencia, obtener_metricas, entrenar_modelo

prediccion_bp = Blueprint('prediccion', __name__)


# ── GET /prediccion/metricas ───────────────────────────────────
@prediccion_bp.route('/prediccion/metricas', methods=['GET'])
def metricas_modelo():
    """Retorna las métricas de rendimiento del modelo ML."""
    try:
        metricas = obtener_metricas()
        return jsonify({'metricas': metricas}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ── GET /prediccion/:destino_id ────────────────────────────────
@prediccion_bp.route('/prediccion/<string:destino_id>', methods=['GET'])
def predecir_destino(destino_id):
    """
    Predice la afluencia de un destino para un día y mes dados.
    Query params:
        dia  : 0-6 (0=lunes, 6=domingo) — default: día actual
        mes  : 1-12 — default: mes actual
    """
    try:
        from config.firebase_init import get_db
        db  = get_db()
        doc = db.collection('destinos').document(destino_id).get()

        if not doc.exists:
            return jsonify({'error': 'Destino no encontrado'}), 404

        data      = doc.to_dict()
        categoria = data.get('categoria', 'Natural')
        capacidad = data.get('capacidad_max', 300)

        # Parámetros de consulta (default: hoy)
        hoy = datetime.now()
        dia = int(request.args.get('dia', hoy.weekday()))
        mes = int(request.args.get('mes', hoy.month))

        # Normalizar categoría para el encoder
        cat_norm = categoria if categoria in ['Natural', 'Cultural', 'Historico'] else 'Natural'
        if categoria == 'Histórico':
            cat_norm = 'Historico'

        resultado = predecir_afluencia(dia, mes, cat_norm, capacidad)
        resultado['destino_id']     = destino_id
        resultado['destino_nombre'] = data.get('nombre', '')

        return jsonify(resultado), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ── POST /prediccion/entrenar ──────────────────────────────────
@prediccion_bp.route('/prediccion/entrenar', methods=['POST'])
def reentrenar():
    """
    Reentrena el modelo ML leyendo los datos actuales de Firestore.
    Llamar este endpoint cada vez que se registren nuevas visitas
    para que el modelo aprenda de datos reales.
    """
    try:
        metricas = entrenar_modelo()
        return jsonify({
            'mensaje':  'Modelo reentrenado con datos de Firestore',
            'metricas': metricas
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ── GET /prediccion/datos-bd ───────────────────────────────────
@prediccion_bp.route('/prediccion/datos-bd', methods=['GET'])
def resumen_datos_bd():
    """
    Muestra un resumen de los datos reales extraídos de Firestore
    que se usaron para entrenar el modelo ML.
    Útil para demostrar en el video que el ML usa la BD real.
    """
    try:
        from config.firebase_init import get_db
        from collections import defaultdict

        db = get_db()

        # Contar visitas por destino
        visitas_docs = list(db.collection('visitas').stream())
        destinos_docs = list(db.collection('destinos').stream())

        destinos_map = {}
        for doc in destinos_docs:
            d = doc.to_dict()
            destinos_map[doc.id] = {
                'nombre':    d.get('nombre', ''),
                'categoria': d.get('categoria', ''),
                'capacidad': d.get('capacidad_max', 0),
            }

        resumen_destinos = defaultdict(lambda: {'total_visitas': 0, 'total_visitantes': 0})
        for doc in visitas_docs:
            v = doc.to_dict()
            did = v.get('destino_id', '')
            if did:
                resumen_destinos[did]['total_visitas']    += 1
                resumen_destinos[did]['total_visitantes'] += v.get('cantidad', 1)

        detalle = []
        for did, stats in resumen_destinos.items():
            info = destinos_map.get(did, {})
            detalle.append({
                'destino_id':       did,
                'nombre':           info.get('nombre', did),
                'categoria':        info.get('categoria', ''),
                'capacidad_max':    info.get('capacidad', 0),
                'total_visitas':    stats['total_visitas'],
                'total_visitantes': stats['total_visitantes'],
            })

        detalle.sort(key=lambda x: x['total_visitantes'], reverse=True)

        metricas_actuales = obtener_metricas()

        return jsonify({
            'resumen': {
                'total_registros_visitas':    len(visitas_docs),
                'total_destinos_con_visitas': len(resumen_destinos),
                'datos_reales_en_modelo':     metricas_actuales.get('datos_reales_firestore', 0),
                'fuente_datos':               metricas_actuales.get('fuente_datos', 'No entrenado'),
            },
            'detalle_por_destino': detalle,
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500