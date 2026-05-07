"""
domain/ports/input/
Puertos de entrada — contratos de los casos de uso
que el sistema expone hacia el exterior (API REST, frontend).
"""

from abc import ABC, abstractmethod


class DestinoServicePort(ABC):
    """Casos de uso disponibles para destinos."""

    @abstractmethod
    def listar_destinos(self, categoria=None): pass

    @abstractmethod
    def obtener_destino(self, destino_id): pass

    @abstractmethod
    def registrar_visita(self, destino_id, perfil_id, cantidad): pass

    @abstractmethod
    def registrar_salida(self, destino_id, cantidad): pass


class AlertaServicePort(ABC):
    """Casos de uso disponibles para alertas."""

    @abstractmethod
    def listar_alertas_activas(self): pass

    @abstractmethod
    def resolver_alerta(self, alerta_id): pass


class PerfilServicePort(ABC):
    """Casos de uso disponibles para perfiles."""

    @abstractmethod
    def listar_perfiles(self): pass

    @abstractmethod
    def crear_perfil(self, nombre, nombre_perfil, tipo): pass

    @abstractmethod
    def obtener_perfil(self, perfil_id): pass

    @abstractmethod
    def eliminar_perfil(self, perfil_id): pass
