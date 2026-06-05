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


class PrediccionRepositoryPort(ABC):
    """
    Contrato del repositorio de predicción ML.
    Cualquier implementación (Random Forest, red neuronal, etc.)
    debe cumplir esta interfaz.
    """

    @abstractmethod
    def entrenar(self, datos_reales: list) -> dict:
        """
        Entrena el modelo con los datos provistos.
        datos_reales: lista de [dia_semana, mes, categoria, capacidad, ocupacion_%]
        Retorna métricas del entrenamiento.
        """
        pass

    @abstractmethod
    def predecir(self, dia_semana: int, mes: int, categoria: str, capacidad_max: int) -> dict:
        """
        Predice el % de ocupación.
        Retorna dict con porcentaje, estado, recomendación y métricas.
        """
        pass

    @abstractmethod
    def obtener_metricas(self) -> dict:
        """Retorna las métricas del último entrenamiento."""
        pass

    @abstractmethod
    def modelo_listo(self) -> bool:
        """Indica si el modelo ya fue entrenado y está listo para predecir."""
        pass


class VisitaRepositoryPort(ABC):
    """
    Contrato para leer datos de visitas históricos
    (usados para entrenar el modelo ML).
    """

    @abstractmethod
    def listar_para_entrenamiento(self) -> list:
        """
        Retorna lista de registros para entrenamiento:
        [dia_semana, mes, categoria, capacidad_max, ocupacion_%]
        """
        pass

    @abstractmethod
    def resumen_por_destino(self) -> list:
        """
        Retorna resumen de visitas agrupado por destino,
        con total de visitas y visitantes.
        """
        pass


class ReporteRepositoryPort(ABC):
    """
    Puerto de salida para reportes analíticos usando SQL.
    Implementado por SQLiteReporteRepository.
    """

    @abstractmethod
    def inicializar_bd(self) -> None:
        """Crea las tablas y stored procedures (triggers/views) si no existen."""
        pass

    @abstractmethod
    def registrar_visita(self, destino_id: str, destino_nombre: str,
                         categoria: str, capacidad_max: int,
                         perfil_id: str, cantidad: int, fecha: str) -> None:
        """Inserta una visita en el historial SQL."""
        pass

    @abstractmethod
    def sp_afluencia_por_destino(self) -> list:
        """
        Stored procedure: resumen de afluencia total por destino.
        Retorna lista de dicts con destino, categoria, total_visitas, total_visitantes.
        """
        pass

    @abstractmethod
    def sp_afluencia_por_mes(self, destino_id: str = None) -> list:
        """
        Stored procedure: afluencia agrupada por mes.
        Si se pasa destino_id filtra por ese destino.
        """
        pass

    @abstractmethod
    def sp_ranking_dias_semana(self, destino_id: str = None) -> list:
        """
        Stored procedure: ranking de días de la semana por afluencia promedio.
        """
        pass

    @abstractmethod
    def sp_ocupacion_promedio_categoria(self) -> list:
        """
        Stored procedure: % de ocupación promedio por categoría de destino.
        """
        pass

    @abstractmethod
    def sp_historial_visitas(self, destino_id: str = None,
                              limit: int = 50) -> list:
        """
        Stored procedure: historial de visitas con JOIN a destinos.
        """
        pass
