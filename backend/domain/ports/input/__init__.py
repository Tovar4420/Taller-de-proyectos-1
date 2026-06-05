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


class PrediccionServicePort(ABC):
    """Casos de uso disponibles para predicción ML de afluencia."""

    @abstractmethod
    def predecir_afluencia(self, destino_id: str, dia_semana: int, mes: int) -> dict:
        """Predice el % de ocupación de un destino para un día y mes dados."""
        pass

    @abstractmethod
    def obtener_metricas(self) -> dict:
        """Retorna las métricas de rendimiento del modelo ML."""
        pass

    @abstractmethod
    def reentrenar_modelo(self) -> dict:
        """Reentrena el modelo con los datos actuales de la BD."""
        pass

    @abstractmethod
    def resumen_datos_bd(self) -> dict:
        """Retorna un resumen de los datos usados para entrenar el modelo."""
        pass

    @abstractmethod
    def mejores_dias_visita(self, destino_id: str, mes: int) -> dict:
        """
        Caso de uso ML 2: predice la ocupación para los 7 días de la semana
        y retorna un ranking ordenado de mejor a peor día para visitar.
        """
        pass
