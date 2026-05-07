"""
application/use_cases/
Casos de uso — orquestan el dominio y los repositorios.
Implementan los puertos de entrada (DestinoServicePort, etc.)
y usan los puertos de salida (repositorios) para persistir datos.
"""

from domain.entities import Destino, Alerta, Perfil
from domain.ports.input import DestinoServicePort, AlertaServicePort, PerfilServicePort
from infrastructure.adapters.output.database import (
    FirestoreDestinoRepository,
    FirestoreAlertaRepository,
    FirestorePerfilRepository,
)


class DestinoUseCase(DestinoServicePort):
    """Caso de uso: gestión de destinos turísticos."""

    def __init__(self):
        self._destino_repo = FirestoreDestinoRepository()
        self._alerta_repo  = FirestoreAlertaRepository()

    def listar_destinos(self, categoria=None):
        docs = self._destino_repo.listar_todos(categoria)
        destinos = [self._doc_to_entidad(d) for d in docs]
        destinos.sort(key=lambda x: x.nombre)
        return [d.to_dict() for d in destinos]

    def obtener_destino(self, destino_id):
        doc = self._destino_repo.obtener_por_id(destino_id)
        if not doc:
            return None
        return self._doc_to_entidad(doc).to_dict()

    def registrar_visita(self, destino_id, perfil_id, cantidad=1):
        doc = self._destino_repo.obtener_por_id(destino_id)
        if not doc:
            raise ValueError('Destino no encontrado')

        destino = self._doc_to_entidad(doc)

        # Regla de negocio: verificar capacidad
        if not destino.puede_recibir(cantidad):
            raise OverflowError('Capacidad máxima alcanzada')

        nuevos = destino.visitantes_actuales + cantidad
        self._destino_repo.actualizar_visitantes(destino_id, nuevos)
        self._destino_repo.registrar_visita(destino_id, perfil_id, cantidad)

        # Actualizar entidad y verificar si necesita alerta
        destino.visitantes_actuales = nuevos
        self._verificar_alerta(destino)

        doc_actualizado = self._destino_repo.obtener_por_id(destino_id)
        return self._doc_to_entidad(doc_actualizado).to_dict()

    def registrar_salida(self, destino_id, cantidad=1):
        doc = self._destino_repo.obtener_por_id(destino_id)
        if not doc:
            raise ValueError('Destino no encontrado')
        destino = self._doc_to_entidad(doc)
        nuevos  = max(0, destino.visitantes_actuales - cantidad)
        self._destino_repo.actualizar_visitantes(destino_id, nuevos)
        doc_actualizado = self._destino_repo.obtener_por_id(destino_id)
        return self._doc_to_entidad(doc_actualizado).to_dict()

    def _verificar_alerta(self, destino: Destino):
        tipo = destino.tipo_alerta_necesaria()
        if not tipo:
            return
        if self._alerta_repo.existe_activa(destino.id, tipo):
            return
        if tipo == 'critica':
            msg = f"{destino.nombre} ha alcanzado el {destino.porcentaje_ocupacion}% de capacidad. Acceso restringido recomendado."
        else:
            msg = f"{destino.nombre} está al {destino.porcentaje_ocupacion}% de capacidad. Se recomienda visitar destinos alternativos."
        self._alerta_repo.crear(destino.id, destino.nombre, tipo, msg)

    def _doc_to_entidad(self, doc) -> Destino:
        return Destino(
            id=doc['id'],
            nombre=doc.get('nombre'),
            ubicacion=doc.get('ubicacion'),
            descripcion=doc.get('descripcion'),
            categoria=doc.get('categoria'),
            capacidad_max=doc.get('capacidad_max', 0),
            visitantes_actuales=doc.get('visitantes_actuales', 0),
            latitud=doc.get('latitud'),
            longitud=doc.get('longitud'),
        )


class AlertaUseCase(AlertaServicePort):
    """Caso de uso: gestión de alertas de capacidad."""

    def __init__(self):
        self._repo = FirestoreAlertaRepository()

    def listar_alertas_activas(self):
        alertas = self._repo.listar_activas()
        return sorted(alertas, key=lambda x: x.get('fecha', ''), reverse=True)

    def resolver_alerta(self, alerta_id):
        self._repo.desactivar(alerta_id)


class PerfilUseCase(PerfilServicePort):
    """Caso de uso: gestión de perfiles de usuario."""

    def __init__(self):
        self._repo = FirestorePerfilRepository()

    def listar_perfiles(self):
        docs = self._repo.listar_todos()
        result = []
        for d in docs:
            total = self._repo.contar_visitas(d['id'])
            perfil = Perfil(
                id=d['id'], nombre=d.get('nombre'),
                nombre_perfil=d.get('nombre_perfil'),
                tipo=d.get('tipo', 'turista'),
                fecha_creacion=d.get('fecha_creacion'),
                total_visitas=total
            )
            result.append(perfil.to_dict())
        return sorted(result, key=lambda x: x['nombre_perfil'])

    def crear_perfil(self, nombre, nombre_perfil, tipo='turista'):
        if self._repo.existe_nombre_perfil(nombre_perfil):
            raise ValueError('El nombre de perfil ya existe')
        doc = self._repo.crear(nombre, nombre_perfil, tipo)
        return Perfil(
            id=doc['id'], nombre=nombre,
            nombre_perfil=nombre_perfil, tipo=tipo,
            fecha_creacion=doc.get('fecha_creacion'), total_visitas=0
        ).to_dict()

    def obtener_perfil(self, perfil_id):
        doc = self._repo.obtener_por_id(perfil_id)
        if not doc:
            return None
        total = self._repo.contar_visitas(perfil_id)
        return Perfil(
            id=doc['id'], nombre=doc.get('nombre'),
            nombre_perfil=doc.get('nombre_perfil'),
            tipo=doc.get('tipo', 'turista'),
            fecha_creacion=doc.get('fecha_creacion'),
            total_visitas=total
        ).to_dict()

    def eliminar_perfil(self, perfil_id):
        doc = self._repo.obtener_por_id(perfil_id)
        if not doc:
            raise ValueError('Perfil no encontrado')
        nombre = doc.get('nombre_perfil', '')
        self._repo.eliminar(perfil_id)
        return nombre
