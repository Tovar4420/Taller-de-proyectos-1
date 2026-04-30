"""
app.py
Aplicación Flask - Sistema de Turismo Sostenible Junín
Backend con Firebase Firestore (reemplaza SQLite + SQLAlchemy)
"""

from flask import Flask
from flask_cors import CORS
from config.firebase_init import init_firebase
from config.seed_data import seed_destinos
from error_handlers import register_error_handlers

# Rutas
from routes.destinos import destinos_bp
from routes.perfiles import perfiles_bp
from routes.alertas import alertas_bp

app = Flask(__name__)
CORS(app)

# Inicializar Firebase
init_firebase()
seed_destinos()

# Manejadores de error
register_error_handlers(app)

# Registrar blueprints
app.register_blueprint(destinos_bp)
app.register_blueprint(perfiles_bp)
app.register_blueprint(alertas_bp)

if __name__ == '__main__':
    print("\n" + "="*50)
    print("🌿 SISTEMA TURISMO SOSTENIBLE - JUNÍN")
    print("="*50)
    print("🔥 Base de datos: Firebase Firestore")
    print("🌐 URL: http://localhost:5000")
    print("="*50)
    print("\n📋 ENDPOINTS DISPONIBLES:")
    print("  GET    /destinos              - Listar destinos")
    print("  GET    /destinos/:id          - Obtener destino")
    print("  POST   /destinos/:id/visita   - Registrar visita")
    print("  POST   /destinos/:id/salida   - Registrar salida")
    print("  GET    /perfiles              - Listar perfiles")
    print("  POST   /perfiles              - Crear perfil")
    print("  GET    /perfiles/:id          - Obtener perfil")
    print("  DELETE /perfiles/:id          - Eliminar perfil")
    print("  GET    /alertas               - Ver alertas activas")
    print("  DELETE /alertas/:id           - Resolver alerta")
    print("  GET    /health                - Estado del servidor")
    print("="*50 + "\n")
    app.run(debug=True, port=5000)
