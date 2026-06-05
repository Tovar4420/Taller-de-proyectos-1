"""
domain/entities/
Entidades del dominio — lógica de negocio pura sin dependencias externas.
"""

from datetime import datetime, timezone


class Destino:
    """Entidad de dominio: Destino turístico."""

    UMBRAL_ADVERTENCIA = 70
    UMBRAL_CRITICO     = 90

    def __init__(self, id, nombre, ubicacion, descripcion,
                 categoria, capacidad_max, visitantes_actuales,
                 latitud=None, longitud=None):
        self.id                  = id
        self.nombre              = nombre
        self.ubicacion           = ubicacion
        self.descripcion         = descripcion
        self.categoria           = categoria
        self.capacidad_max       = capacidad_max
        self.visitantes_actuales = visitantes_actuales
        self.latitud             = latitud
        self.longitud            = longitud

    @property
    def porcentaje_ocupacion(self):
        if self.capacidad_max == 0:
            return 0
        return round((self.visitantes_actuales / self.capacidad_max) * 100, 1)

    @property
    def estado(self):
        pct = self.porcentaje_ocupacion
        if pct >= self.UMBRAL_CRITICO:   return 'critico'
        elif pct >= self.UMBRAL_ADVERTENCIA: return 'alto'
        elif pct >= 40:                  return 'moderado'
        return 'bajo'

    def puede_recibir(self, cantidad=1):
        """Regla de negocio: verifica si hay capacidad."""
        return (self.visitantes_actuales + cantidad) <= self.capacidad_max

    def tipo_alerta_necesaria(self):
        """Regla de negocio: qué tipo de alerta generar."""
        pct = self.porcentaje_ocupacion
        if pct >= self.UMBRAL_CRITICO:       return 'critica'
        elif pct >= self.UMBRAL_ADVERTENCIA: return 'advertencia'
        return None

    def to_dict(self):
        return {
            'id':                   self.id,
            'nombre':               self.nombre,
            'ubicacion':            self.ubicacion,
            'descripcion':          self.descripcion,
            'categoria':            self.categoria,
            'capacidad_max':        self.capacidad_max,
            'visitantes_actuales':  self.visitantes_actuales,
            'porcentaje_ocupacion': self.porcentaje_ocupacion,
            'estado':               self.estado,
            'latitud':              self.latitud,
            'longitud':             self.longitud,
        }


class Perfil:
    """Entidad de dominio: Perfil de usuario."""

    TIPOS_VALIDOS = ['turista', 'operador', 'admin']

    def __init__(self, id, nombre, nombre_perfil, tipo='turista',
                 fecha_creacion=None, total_visitas=0):
        self.id             = id
        self.nombre         = nombre
        self.nombre_perfil  = nombre_perfil
        self.tipo           = tipo if tipo in self.TIPOS_VALIDOS else 'turista'
        self.fecha_creacion = fecha_creacion
        self.total_visitas  = total_visitas

    def to_dict(self):
        return {
            'id':             self.id,
            'nombre':         self.nombre,
            'nombre_perfil':  self.nombre_perfil,
            'tipo':           self.tipo,
            'fecha_creacion': self.fecha_creacion,
            'total_visitas':  self.total_visitas,
        }


class Alerta:
    """Entidad de dominio: Alerta de capacidad."""

    def __init__(self, id, destino_id, destino, tipo,
                 mensaje, activa=True, fecha=None):
        self.id         = id
        self.destino_id = destino_id
        self.destino    = destino
        self.tipo       = tipo
        self.mensaje    = mensaje
        self.activa     = activa
        self.fecha      = fecha or datetime.now(timezone.utc).isoformat()

    def to_dict(self):
        return {
            'id':         self.id,
            'destino_id': self.destino_id,
            'destino':    self.destino,
            'tipo':       self.tipo,
            'mensaje':    self.mensaje,
            'activa':     self.activa,
            'fecha':      self.fecha,
        }
