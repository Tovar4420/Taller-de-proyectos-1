"""
domain/ports/output/
Puertos de salida — contratos que debe cumplir cualquier
implementación de repositorio (Firestore, PostgreSQL, etc.)
"""

from abc import ABC, abstractmethod


class DestinoRepositoryPort(ABC):
    """Contrato del repositorio de destinos."""

    @abstractmethod
    def listar_todos(self, categoria=None): pass

    @abstractmethod
    def obtener_por_id(self, destino_id): pass

    @abstractmethod
    def actualizar_visitantes(self, destino_id, nuevos_visitantes): pass

    @abstractmethod
    def registrar_visita(self, destino_id, perfil_id, cantidad): pass


class AlertaRepositoryPort(ABC):
    """Contrato del repositorio de alertas."""

    @abstractmethod
    def listar_activas(self): pass

    @abstractmethod
    def crear(self, destino_id, nombre, tipo, mensaje): pass

    @abstractmethod
    def existe_activa(self, destino_id, tipo): pass

    @abstractmethod
    def desactivar(self, alerta_id): pass


class PerfilRepositoryPort(ABC):
    """Contrato del repositorio de perfiles."""

    @abstractmethod
    def listar_todos(self): pass

    @abstractmethod
    def obtener_por_id(self, perfil_id): pass

    @abstractmethod
    def crear(self, nombre, nombre_perfil, tipo): pass

    @abstractmethod
    def eliminar(self, perfil_id): pass

    @abstractmethod
    def existe_nombre_perfil(self, nombre_perfil): pass

    @abstractmethod
    def contar_visitas(self, perfil_id): pass
