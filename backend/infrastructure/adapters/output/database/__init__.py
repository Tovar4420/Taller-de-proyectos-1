"""
infrastructure/adapters/output/database/
Adaptador de salida — implementa los puertos de repositorio
usando Firebase Firestore como tecnología de persistencia.
Si en el futuro se cambia a PostgreSQL, solo se modifica este archivo.
"""

from datetime import datetime, timezone
from config.firebase_init import get_db
from domain.ports.output import (
    DestinoRepositoryPort,
    AlertaRepositoryPort,
    PerfilRepositoryPort
)


class FirestoreDestinoRepository(DestinoRepositoryPort):
    """Implementación Firestore del repositorio de destinos."""

    def listar_todos(self, categoria=None):
        db    = get_db()
        query = db.collection('destinos')
        if categoria:
            query = query.where('categoria', '==', categoria)
        return [{'id': d.id, **d.to_dict()} for d in query.stream()]

    def obtener_por_id(self, destino_id):
        db  = get_db()
        doc = db.collection('destinos').document(destino_id).get()
        if not doc.exists:
            return None
        return {'id': doc.id, **doc.to_dict()}

    def actualizar_visitantes(self, destino_id, nuevos_visitantes):
        db = get_db()
        db.collection('destinos').document(destino_id).update(
            {'visitantes_actuales': nuevos_visitantes}
        )

    def registrar_visita(self, destino_id, perfil_id, cantidad):
        db = get_db()
        db.collection('visitas').add({
            'destino_id': destino_id,
            'perfil_id':  perfil_id,
            'cantidad':   cantidad,
            'fecha':      datetime.now(timezone.utc).isoformat(),
        })


class FirestoreAlertaRepository(AlertaRepositoryPort):
    """Implementación Firestore del repositorio de alertas."""

    def listar_activas(self):
        db   = get_db()
        docs = db.collection('alertas').where('activa', '==', True).stream()
        return [{'id': d.id, **d.to_dict()} for d in docs]

    def crear(self, destino_id, nombre, tipo, mensaje):
        db = get_db()
        db.collection('alertas').add({
            'destino_id': destino_id,
            'destino':    nombre,
            'tipo':       tipo,
            'mensaje':    mensaje,
            'activa':     True,
            'fecha':      datetime.now(timezone.utc).isoformat(),
        })

    def existe_activa(self, destino_id, tipo):
        db   = get_db()
        docs = (
            db.collection('alertas')
            .where('destino_id', '==', destino_id)
            .where('tipo', '==', tipo)
            .where('activa', '==', True)
            .limit(1)
            .stream()
        )
        return bool(list(docs))

    def desactivar(self, alerta_id):
        db = get_db()
        db.collection('alertas').document(alerta_id).update({'activa': False})


class FirestorePerfilRepository(PerfilRepositoryPort):
    """Implementación Firestore del repositorio de perfiles."""

    def listar_todos(self):
        db   = get_db()
        docs = db.collection('perfiles').stream()
        return [{'id': d.id, **d.to_dict()} for d in docs]

    def obtener_por_id(self, perfil_id):
        db  = get_db()
        doc = db.collection('perfiles').document(perfil_id).get()
        if not doc.exists:
            return None
        return {'id': doc.id, **doc.to_dict()}

    def crear(self, nombre, nombre_perfil, tipo='turista'):
        db   = get_db()
        data = {
            'nombre':         nombre,
            'nombre_perfil':  nombre_perfil,
            'tipo':           tipo,
            'fecha_creacion': datetime.now(timezone.utc).isoformat(),
        }
        _, ref = db.collection('perfiles').add(data)
        return {'id': ref.id, **data}

    def eliminar(self, perfil_id):
        db = get_db()
        db.collection('perfiles').document(perfil_id).delete()

    def existe_nombre_perfil(self, nombre_perfil):
        db   = get_db()
        docs = (
            db.collection('perfiles')
            .where('nombre_perfil', '==', nombre_perfil)
            .limit(1)
            .stream()
        )
        return bool(list(docs))

    def contar_visitas(self, perfil_id):
        db      = get_db()
        visitas = db.collection('visitas').where('perfil_id', '==', perfil_id).stream()
        return sum(1 for _ in visitas)
