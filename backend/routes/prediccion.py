"""
routes/prediccion.py
Adaptador de entrada HTTP para prediccion de afluencia ML.
Solo maneja HTTP — toda la logica esta en PrediccionUseCase.
"""

from flask import Blueprint, jsonify, request
from datetime import datetime
from application.use_cases import PrediccionUseCase

prediccion_bp = Blueprint('prediccion', __name__)
_use_case     = PrediccionUseCase()


@prediccion_bp.route('/prediccion/metricas', methods=['GET'])
def metricas_modelo():
    """Retorna las metricas de rendimiento del modelo ML."""
    try:
        metricas = _use_case.obtener_metricas()
        return jsonify({'metricas': metricas}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@prediccion_bp.route('/prediccion/<string:destino_id>', methods=['GET'])
def predecir_destino(destino_id):
    """
    Predice la afluencia de un destino para un dia y mes dados.
    Query params:
        dia : 0-6 (0=lunes, 6=domingo) — default: dia actual
        mes : 1-12                      — default: mes actual
    """
    try:
        hoy = datetime.now()
        dia = int(request.args.get('dia', hoy.weekday()))
        mes = int(request.args.get('mes', hoy.month))

        resultado = _use_case.predecir_afluencia(destino_id, dia, mes)
        return jsonify(resultado), 200

    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@prediccion_bp.route('/prediccion/entrenar', methods=['POST'])
def reentrenar():
    """Reentrena el modelo ML con los datos actuales de Firestore."""
    try:
        metricas = _use_case.reentrenar_modelo()
        return jsonify({
            'mensaje':  'Modelo reentrenado con datos de Firestore',
            'metricas': metricas,
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@prediccion_bp.route('/prediccion/datos-bd', methods=['GET'])
def resumen_datos_bd():
    """Muestra el resumen de datos de Firestore usados para entrenar el modelo."""
    try:
        resumen = _use_case.resumen_datos_bd()
        return jsonify(resumen), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@prediccion_bp.route('/prediccion/<string:destino_id>/mejores-dias', methods=['GET'])
def mejores_dias(destino_id):
    """
    Caso de uso ML 2: ranking de los 7 días de la semana ordenados
    de mejor a peor para visitar el destino en un mes dado.
    Query param:
        mes : 1-12 — default: mes actual
    """
    try:
        mes = int(request.args.get('mes', datetime.now().month))
        if not 1 <= mes <= 12:
            return jsonify({'error': 'mes debe estar entre 1 y 12'}), 400

        resultado = _use_case.mejores_dias_visita(destino_id, mes)
        return jsonify(resultado), 200

    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500
