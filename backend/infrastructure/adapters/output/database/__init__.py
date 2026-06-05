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
    PerfilRepositoryPort,
    VisitaRepositoryPort,
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


class FirestoreVisitaRepository(VisitaRepositoryPort):
    """
    Implementacion Firestore del repositorio de visitas.
    Provee datos historicos para el entrenamiento del modelo ML.
    """

    def listar_para_entrenamiento(self) -> list:
        """
        Lee visitas y destinos de Firestore y devuelve registros
        en el formato que espera el adaptador ML:
        [dia_semana, mes, categoria, capacidad_max, ocupacion_%]
        """
        from collections import defaultdict
        from datetime import datetime

        db = get_db()

        destinos_ref = db.collection('destinos').stream()
        destinos_map = {}
        for doc in destinos_ref:
            d = doc.to_dict()
            cat = d.get('categoria', 'Natural')
            if cat == 'Historico':
                cat = 'Historico'
            if cat not in ['Natural', 'Cultural', 'Historico']:
                cat = 'Natural'
            destinos_map[doc.id] = {
                'categoria': cat,
                'capacidad': d.get('capacidad_max', 300),
            }

        if not destinos_map:
            return []

        visitas_raw = []
        for doc in db.collection('visitas').stream():
            v          = doc.to_dict()
            destino_id = v.get('destino_id')
            fecha_str  = v.get('fecha')
            cantidad   = v.get('cantidad', 1)

            if not destino_id or not fecha_str or destino_id not in destinos_map:
                continue
            try:
                fecha      = datetime.fromisoformat(fecha_str.replace('Z', '+00:00'))
                dia_semana = fecha.weekday()
                mes        = fecha.month
            except Exception:
                continue

            visitas_raw.append({
                'destino_id': destino_id,
                'dia_semana': dia_semana,
                'mes':        mes,
                'cantidad':   cantidad,
            })

        if not visitas_raw:
            return []

        agrupado = defaultdict(list)
        for v in visitas_raw:
            agrupado[(v['destino_id'], v['dia_semana'], v['mes'])].append(v['cantidad'])

        registros = []
        for (destino_id, dia, mes), cantidades in agrupado.items():
            info      = destinos_map[destino_id]
            capacidad = info['capacidad']
            categoria = info['categoria']
            pct       = min(100.0, round((sum(cantidades) / capacidad) * 100, 1))
            registros.append([dia, mes, categoria, capacidad, pct])

        return registros

    def resumen_por_destino(self) -> list:
        """Resumen de visitas agrupado por destino."""
        from collections import defaultdict

        db = get_db()

        destinos_map = {
            doc.id: doc.to_dict()
            for doc in db.collection('destinos').stream()
        }

        resumen = defaultdict(lambda: {'total_visitas': 0, 'total_visitantes': 0})
        for doc in db.collection('visitas').stream():
            v   = doc.to_dict()
            did = v.get('destino_id', '')
            if did:
                resumen[did]['total_visitas']    += 1
                resumen[did]['total_visitantes'] += v.get('cantidad', 1)

        detalle = []
        for did, stats in resumen.items():
            info = destinos_map.get(did, {})
            detalle.append({
                'destino_id':       did,
                'nombre':           info.get('nombre', did),
                'categoria':        info.get('categoria', ''),
                'capacidad_max':    info.get('capacidad_max', 0),
                'total_visitas':    stats['total_visitas'],
                'total_visitantes': stats['total_visitantes'],
            })

        return sorted(detalle, key=lambda x: x['total_visitantes'], reverse=True)
