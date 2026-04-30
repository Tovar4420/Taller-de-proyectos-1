"""
config/firebase_init.py
Inicialización de Firebase Admin SDK + Firestore
Reemplaza db_init.py (SQLAlchemy + SQLite)
"""

import os
import firebase_admin
from firebase_admin import credentials, firestore

# Instancia global de Firestore
db = None


def init_firebase():
    """Inicializa Firebase Admin SDK y retorna el cliente Firestore."""
    global db

    if firebase_admin._apps:
        db = firestore.client()
        return db

    cred_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'firebase_credentials.json'
    )

    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)

    db = firestore.client()
    print("✅ Firebase/Firestore inicializado correctamente")
    return db


def get_db():
    """Retorna el cliente Firestore (debe llamarse después de init_firebase)."""
    global db
    if db is None:
        db = firestore.client()
    return db
