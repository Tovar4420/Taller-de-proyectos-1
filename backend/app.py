"""
app.py
Aplicación Flask - Sistema de Turismo Sostenible Junín
Backend con Firebase Firestore + SQLite (Stored Procedures) + Machine Learning
"""

from flask import Flask
from flask_cors import CORS
from config.firebase_init import init_firebase
from config.seed_data import seed_destinos
from error_handlers import register_error_handlers

# Rutas
from routes.destinos   import destinos_bp
from routes.perfiles   import perfiles_bp
from routes.alertas    import alertas_bp
from routes.prediccion import prediccion_bp
from routes.reportes   import reportes_bp

app = Flask(__name__)
CORS(app)

# Inicializar Firebase
init_firebase()
seed_destinos()

# Inicializar SQLite — crea tablas, triggers y vistas (stored procedures)
from infrastructure.adapters.output.database.sqlite_repository import SQLiteReporteRepository
SQLiteReporteRepository().inicializar_bd()

# Manejadores de error
register_error_handlers(app)

# Registrar blueprints
app.register_blueprint(destinos_bp)
app.register_blueprint(perfiles_bp)
app.register_blueprint(alertas_bp)
app.register_blueprint(prediccion_bp)
app.register_blueprint(reportes_bp)

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🌿 SISTEMA TURISMO SOSTENIBLE - JUNÍN")
    print("="*60)
    print("🔥 Base de datos : Firebase Firestore (tiempo real)")
    print("🗄️  Reportes SQL  : SQLite + Stored Procedures")
    print("🤖 ML            : Random Forest Regressor")
    print("🌐 URL           : http://localhost:5000")
    print("="*60)
    print("\n📋 ENDPOINTS FIRESTORE:")
    print("  GET    /destinos                      - Listar destinos")
    print("  GET    /destinos/:id                  - Obtener destino")
    print("  POST   /destinos/:id/visita           - Registrar visita")
    print("  POST   /destinos/:id/salida           - Registrar salida")
    print("  GET    /perfiles                      - Listar perfiles")
    print("  POST   /perfiles                      - Crear perfil")
    print("  GET    /perfiles/:id                  - Obtener perfil")
    print("  DELETE /perfiles/:id                  - Eliminar perfil")
    print("  GET    /alertas                       - Ver alertas activas")
    print("  DELETE /alertas/:id                   - Resolver alerta")
    print("  GET    /prediccion/:id                - Predecir afluencia ML")
    print("  GET    /prediccion/metricas           - Métricas del modelo")
    print("  GET    /prediccion/:id/mejores-dias   - ML caso 2: ranking mejores días")
    print("  POST   /prediccion/entrenar           - Reentrenar modelo")
    print("  GET    /health                        - Estado del servidor")
    print("\n📊 ENDPOINTS SQLITE (Stored Procedures):")
    print("  GET    /reportes/afluencia-destinos   - SP: resumen por destino")
    print("  GET    /reportes/afluencia-mensual    - SP: afluencia por mes")
    print("  GET    /reportes/ranking-dias         - SP: ranking días semana")
    print("  GET    /reportes/ocupacion-categoria  - SP: ocupación por categoría")
    print("  GET    /reportes/historial            - SP: historial de visitas")
    print("="*60 + "\n")
    app.run(debug=True, port=5000)
