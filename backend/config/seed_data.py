"""
config/seed_data.py
Carga los destinos iniciales en Firestore si la colección está vacía.
"""

from datetime import datetime, timezone
from config.firebase_init import get_db


DESTINOS_INICIALES = [
    {
        "nombre": "Gruta de Huagapo",
        "ubicacion": "Palcamayo, Tarma",
        "descripcion": "Una de las cavernas inundadas más largas de Sudamérica, con formaciones kársticas únicas.",
        "categoria": "Natural",
        "capacidad_max": 483,
        "visitantes_actuales": 0,
        "latitud": -11.2833,
        "longitud": -75.6167,
        "fecha_creacion": datetime.now(timezone.utc).isoformat(),
    },
    {
        "nombre": "Nevado Huaytapallana",
        "ubicacion": "Huancayo",
        "descripcion": "Glaciar sagrado de los Wankas, fuente de agua para la región y destino de montañismo.",
        "categoria": "Natural",
        "capacidad_max": 300,
        "visitantes_actuales": 0,
        "latitud": -11.9833,
        "longitud": -75.0833,
        "fecha_creacion": datetime.now(timezone.utc).isoformat(),
    },
    {
        "nombre": "Laguna de Paca",
        "ubicacion": "Jauja",
        "descripcion": "Laguna de aguas tranquilas rodeada de totorales, ideal para paseos en bote.",
        "categoria": "Natural",
        "capacidad_max": 500,
        "visitantes_actuales": 0,
        "latitud": -11.7833,
        "longitud": -75.4833,
        "fecha_creacion": datetime.now(timezone.utc).isoformat(),
    },
    {
        "nombre": "Valle del Perené",
        "ubicacion": "Chanchamayo",
        "descripcion": "Valle tropical con cafetales, cascadas y comunidades nativas asháninka.",
        "categoria": "Cultural",
        "capacidad_max": 1000,
        "visitantes_actuales": 0,
        "latitud": -10.9667,
        "longitud": -75.2500,
        "fecha_creacion": datetime.now(timezone.utc).isoformat(),
    },
    {
        "nombre": "Convento de Ocopa",
        "ubicacion": "Concepción",
        "descripcion": "Convento franciscano del siglo XVIII con una de las bibliotecas más antiguas del Perú.",
        "categoria": "Histórico",
        "capacidad_max": 200,
        "visitantes_actuales": 0,
        "latitud": -11.9167,
        "longitud": -75.3167,
        "fecha_creacion": datetime.now(timezone.utc).isoformat(),
    },
    {
        "nombre": "Reserva de Junín",
        "ubicacion": "Junín",
        "descripcion": "Lago de altura que alberga el zambullidor de Junín, ave endémica en peligro de extinción.",
        "categoria": "Natural",
        "capacidad_max": 400,
        "visitantes_actuales": 0,
        "latitud": -11.0333,
        "longitud": -76.1833,
        "fecha_creacion": datetime.now(timezone.utc).isoformat(),
    },
]


def seed_destinos():
    """Carga destinos iniciales si la colección está vacía."""
    db = get_db()
    col = db.collection("destinos")
    docs = list(col.limit(1).stream())

    if docs:
        print("ℹ️  Destinos ya existen en Firestore, omitiendo seed.")
        return

    for destino in DESTINOS_INICIALES:
        col.add(destino)

    print(f"🌱 {len(DESTINOS_INICIALES)} destinos iniciales cargados en Firestore.")
