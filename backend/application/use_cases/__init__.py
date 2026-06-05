from datetime import datetime, timezone
"""
application/use_cases/
Casos de uso — orquestan el dominio y los repositorios.
Implementan los puertos de entrada (DestinoServicePort, etc.)
y usan los puertos de salida (repositorios) para persistir datos.
"""

from domain.entities import Destino, Alerta, Perfil
from domain.ports.input import DestinoServicePort, AlertaServicePort, PerfilServicePort, PrediccionServicePort
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
        from infrastructure.adapters.output.database.sqlite_repository import SQLiteReporteRepository
        self._sqlite_repo  = SQLiteReporteRepository()

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

        # Dual-write: guardar también en SQLite para stored procedures
        try:
            self._sqlite_repo.registrar_visita(
                destino_id    = destino_id,
                destino_nombre= destino.nombre,
                categoria     = destino.categoria,
                capacidad_max = destino.capacidad_max,
                perfil_id     = perfil_id,
                cantidad      = cantidad,
                fecha         = datetime.now(timezone.utc).isoformat(),
            )
        except Exception as e:
            print(f"[SQLite] advertencia al guardar visita: {e}")

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


class PrediccionUseCase(PrediccionServicePort):
    """
    Caso de uso: prediccion de afluencia turistica con ML.

    Orquesta el flujo:
    1. Lee datos historicos via VisitaRepositoryPort
    2. Entrena el modelo via PrediccionRepositoryPort
    3. Consulta destinos via DestinoRepositoryPort
    4. Retorna predicciones y metricas
    """

    def __init__(self):
        from infrastructure.adapters.output.ml import RandomForestPrediccionAdapter
        from infrastructure.adapters.output.database import (
            FirestoreVisitaRepository,
            FirestoreDestinoRepository,
        )
        self._prediccion_repo = RandomForestPrediccionAdapter()
        self._visita_repo     = FirestoreVisitaRepository()
        self._destino_repo    = FirestoreDestinoRepository()

    def _asegurar_modelo_entrenado(self):
        """Entrena el modelo si aun no ha sido entrenado."""
        if not self._prediccion_repo.modelo_listo():
            datos = self._visita_repo.listar_para_entrenamiento()
            self._prediccion_repo.entrenar(datos)

    def predecir_afluencia(self, destino_id: str, dia_semana: int, mes: int) -> dict:
        """
        Predice el % de ocupacion de un destino para un dia y mes dados.
        Obtiene categoria y capacidad desde el repositorio de destinos.
        """
        doc = self._destino_repo.obtener_por_id(destino_id)
        if not doc:
            raise ValueError('Destino no encontrado')

        categoria = doc.get('categoria', 'Natural')
        if categoria == 'Historico':
            categoria = 'Historico'
        if categoria not in ['Natural', 'Cultural', 'Historico']:
            categoria = 'Natural'

        capacidad = doc.get('capacidad_max', 300)

        self._asegurar_modelo_entrenado()

        resultado = self._prediccion_repo.predecir(dia_semana, mes, categoria, capacidad)
        resultado['destino_id']     = destino_id
        resultado['destino_nombre'] = doc.get('nombre', '')
        return resultado

    def obtener_metricas(self) -> dict:
        """Retorna las metricas del modelo, entrenandolo si es necesario."""
        self._asegurar_modelo_entrenado()
        return self._prediccion_repo.obtener_metricas()

    def reentrenar_modelo(self) -> dict:
        """Reentrena el modelo con los datos actuales de Firestore."""
        datos = self._visita_repo.listar_para_entrenamiento()
        return self._prediccion_repo.entrenar(datos)

    def resumen_datos_bd(self) -> dict:
        """Retorna resumen de datos de Firestore usados para entrenar."""
        detalle  = self._visita_repo.resumen_por_destino()
        metricas = self._prediccion_repo.obtener_metricas()

        return {
            'resumen': {
                'total_destinos_con_visitas': len(detalle),
                'datos_reales_en_modelo':     metricas.get('datos_reales_firestore', 0),
                'fuente_datos':               metricas.get('fuente_datos', 'No entrenado'),
            },
            'detalle_por_destino': detalle,
        }

    def mejores_dias_visita(self, destino_id: str, mes: int) -> dict:
        """
        Caso de uso ML 2: ranking de mejores días para visitar un destino.
        Llama al modelo 7 veces (una por día de la semana) para el mes dado,
        ordena los resultados de menor a mayor ocupación predicha y
        asigna etiquetas de recomendación.
        """
        doc = self._destino_repo.obtener_por_id(destino_id)
        if not doc:
            raise ValueError('Destino no encontrado')

        categoria = doc.get('categoria', 'Natural')
        if categoria not in ['Natural', 'Cultural', 'Historico']:
            categoria = 'Natural'
        capacidad = doc.get('capacidad_max', 300)

        self._asegurar_modelo_entrenado()

        DIAS = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
        MESES = ['', 'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
                 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']

        ranking = []
        for dia_num, dia_nombre in enumerate(DIAS):
            pred = self._prediccion_repo.predecir(dia_num, mes, categoria, capacidad)
            pct  = pred.get('porcentaje_predicho', 0)

            if pct < 40:
                recomendacion = 'Ideal'
                color         = 'verde'
                icono         = '🟢'
            elif pct < 60:
                recomendacion = 'Bueno'
                color         = 'verde_claro'
                icono         = '🟡'
            elif pct < 75:
                recomendacion = 'Regular'
                color         = 'amarillo'
                icono         = '🟠'
            else:
                recomendacion = 'Evitar'
                color         = 'rojo'
                icono         = '🔴'

            ranking.append({
                'dia_num':          dia_num,
                'dia':              dia_nombre,
                'ocupacion_predicha': round(pct, 1),
                'recomendacion':    recomendacion,
                'color':            color,
                'icono':            icono,
            })

        # Ordenar de menor a mayor ocupación
        ranking.sort(key=lambda x: x['ocupacion_predicha'])

        # Etiquetar posición
        ranking[0]['etiqueta']  = 'Mejor día'
        ranking[-1]['etiqueta'] = 'Día más concurrido'
        for item in ranking[1:-1]:
            item['etiqueta'] = ''

        return {
            'destino_id':     destino_id,
            'destino_nombre': doc.get('nombre', ''),
            'categoria':      categoria,
            'mes':            mes,
            'nombre_mes':     MESES[mes] if 1 <= mes <= 12 else '',
            'caso_uso':       'Ranking de mejores días para visitar',
            'modelo':         'Random Forest Regressor',
            'ranking':        ranking,
            'resumen': {
                'mejor_dia':    ranking[0]['dia'],
                'peor_dia':     ranking[-1]['dia'],
                'dias_ideales': [r['dia'] for r in ranking if r['recomendacion'] == 'Ideal'],
                'dias_evitar':  [r['dia'] for r in ranking if r['recomendacion'] == 'Evitar'],
            }
        }


class ReporteUseCase:
    """
    Caso de uso: reportes analíticos desde SQLite.
    Orquesta los stored procedures del repositorio SQL.
    """

    def __init__(self):
        from infrastructure.adapters.output.database.sqlite_repository import SQLiteReporteRepository
        self._repo = SQLiteReporteRepository()

    def afluencia_por_destino(self) -> list:
        return self._repo.sp_afluencia_por_destino()

    def afluencia_por_mes(self, destino_id: str = None) -> list:
        return self._repo.sp_afluencia_por_mes(destino_id)

    def ranking_dias_semana(self, destino_id: str = None) -> list:
        return self._repo.sp_ranking_dias_semana(destino_id)

    def ocupacion_por_categoria(self) -> list:
        return self._repo.sp_ocupacion_promedio_categoria()

    def historial_visitas(self, destino_id: str = None, limit: int = 50) -> list:
        return self._repo.sp_historial_visitas(destino_id, limit)
