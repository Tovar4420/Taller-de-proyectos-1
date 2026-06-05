"""
routes/reportes.py
Adaptador de entrada HTTP para reportes analíticos (SQLite).
Expone los stored procedures como endpoints REST.
"""

from flask import Blueprint, jsonify, request
from application.use_cases import ReporteUseCase

reportes_bp = Blueprint('reportes', __name__)
_use_case   = ReporteUseCase()


@reportes_bp.route('/reportes/afluencia-destinos', methods=['GET'])
def afluencia_por_destino():
    """SP: resumen total de afluencia por destino."""
    try:
        datos = _use_case.afluencia_por_destino()
        return jsonify({'datos': datos, 'total': len(datos),
                        'stored_procedure': 'sp_afluencia_por_destino',
                        'fuente': 'SQLite'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@reportes_bp.route('/reportes/afluencia-mensual', methods=['GET'])
def afluencia_por_mes():
    """SP: afluencia agrupada por mes. Query param: destino_id (opcional)."""
    try:
        destino_id = request.args.get('destino_id')
        datos = _use_case.afluencia_por_mes(destino_id)
        return jsonify({'datos': datos, 'total': len(datos),
                        'stored_procedure': 'vw_afluencia_mensual',
                        'fuente': 'SQLite',
                        'filtro_destino': destino_id}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@reportes_bp.route('/reportes/ranking-dias', methods=['GET'])
def ranking_dias():
    """SP: ranking de días de semana por afluencia. Query param: destino_id (opcional)."""
    try:
        destino_id = request.args.get('destino_id')
        datos = _use_case.ranking_dias_semana(destino_id)
        return jsonify({'datos': datos, 'total': len(datos),
                        'stored_procedure': 'vw_ranking_dias',
                        'fuente': 'SQLite',
                        'filtro_destino': destino_id}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@reportes_bp.route('/reportes/ocupacion-categoria', methods=['GET'])
def ocupacion_categoria():
    """SP: % de ocupación promedio por categoría de destino."""
    try:
        datos = _use_case.ocupacion_por_categoria()
        return jsonify({'datos': datos, 'total': len(datos),
                        'stored_procedure': 'vw_ocupacion_categoria',
                        'fuente': 'SQLite'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@reportes_bp.route('/reportes/historial', methods=['GET'])
def historial_visitas():
    """SP: historial de visitas detallado. Query params: destino_id, limit."""
    try:
        destino_id = request.args.get('destino_id')
        limit = int(request.args.get('limit', 50))
        datos = _use_case.historial_visitas(destino_id, limit)
        return jsonify({'datos': datos, 'total': len(datos),
                        'stored_procedure': 'sp_historial_visitas',
                        'fuente': 'SQLite',
                        'filtro_destino': destino_id}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
