"""
infrastructure/adapters/output/database/sqlite_repository.py
════════════════════════════════════════════════════════════════
Adaptador de salida — SQLite con Stored Procedures.

Implementa ReporteRepositoryPort usando SQLite como motor SQL.
Complementa a Firestore:
  · Firestore  → datos operacionales en tiempo real
  · SQLite     → historial analítico con consultas SQL complejas

Los "stored procedures" en SQLite se implementan como:
  · VISTAs  (CREATE VIEW)   — consultas guardadas y reutilizables
  · TRIGGERs               — lógica automática al insertar
  · Funciones Python        — encapsulan queries complejas con nombre
════════════════════════════════════════════════════════════════
"""

import sqlite3
import os
from datetime import datetime, timezone
from domain.ports.output import ReporteRepositoryPort


# Ruta de la base de datos SQLite (dentro del backend)
_DB_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))),
    'turismo_historico.db'
)


def _get_conn() -> sqlite3.Connection:
    """Retorna una conexión con row_factory para obtener dicts."""
    conn = sqlite3.connect(_DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


class SQLiteReporteRepository(ReporteRepositoryPort):
    """
    Implementación SQLite del repositorio de reportes analíticos.
    Usa VIStas y TRIGGERs como stored procedures.
    Intercambiable por PostgreSQL sin tocar el dominio.
    """

    def inicializar_bd(self) -> None:
        """
        Crea tablas, vistas (stored procedures) y triggers.
        Se llama una sola vez al arrancar la app.
        """
        conn = _get_conn()
        try:
            # ── TABLA PRINCIPAL ───────────────────────────────────────
            conn.execute("""
                CREATE TABLE IF NOT EXISTS visitas_historico (
                    id            INTEGER PRIMARY KEY AUTOINCREMENT,
                    destino_id    TEXT    NOT NULL,
                    destino_nombre TEXT   NOT NULL,
                    categoria     TEXT    NOT NULL,
                    capacidad_max INTEGER NOT NULL,
                    perfil_id     TEXT,
                    cantidad      INTEGER NOT NULL DEFAULT 1,
                    fecha         TEXT    NOT NULL,
                    dia_semana    INTEGER NOT NULL,
                    mes           INTEGER NOT NULL,
                    anio          INTEGER NOT NULL,
                    creado_en     TEXT    DEFAULT (datetime('now'))
                )
            """)

            # ── TABLA DE RESUMEN (actualizada por trigger) ────────────
            conn.execute("""
                CREATE TABLE IF NOT EXISTS resumen_destino (
                    destino_id      TEXT PRIMARY KEY,
                    destino_nombre  TEXT NOT NULL,
                    categoria       TEXT NOT NULL,
                    capacidad_max   INTEGER NOT NULL,
                    total_visitas   INTEGER DEFAULT 0,
                    total_visitantes INTEGER DEFAULT 0,
                    ultima_visita   TEXT
                )
            """)

            # ── TRIGGER: actualiza resumen al insertar visita ─────────
            # Equivalente a un stored procedure de actualización automática
            conn.execute("""
                CREATE TRIGGER IF NOT EXISTS trg_actualizar_resumen
                AFTER INSERT ON visitas_historico
                BEGIN
                    INSERT INTO resumen_destino
                        (destino_id, destino_nombre, categoria, capacidad_max,
                         total_visitas, total_visitantes, ultima_visita)
                    VALUES
                        (NEW.destino_id, NEW.destino_nombre, NEW.categoria,
                         NEW.capacidad_max, 1, NEW.cantidad, NEW.fecha)
                    ON CONFLICT(destino_id) DO UPDATE SET
                        total_visitas    = total_visitas + 1,
                        total_visitantes = total_visitantes + NEW.cantidad,
                        ultima_visita    = NEW.fecha;
                END
            """)

            # ── VISTA 1: afluencia mensual ────────────────────────────
            # Stored procedure: agrupa visitas por mes y año
            conn.execute("""
                CREATE VIEW IF NOT EXISTS vw_afluencia_mensual AS
                SELECT
                    destino_id,
                    destino_nombre,
                    categoria,
                    anio,
                    mes,
                    SUM(cantidad)  AS total_visitantes,
                    COUNT(*)       AS total_visitas,
                    ROUND(AVG(cantidad), 2) AS promedio_por_visita
                FROM visitas_historico
                GROUP BY destino_id, anio, mes
                ORDER BY anio DESC, mes DESC
            """)

            # ── VISTA 2: ranking por día de semana ────────────────────
            # Stored procedure: qué días tienen más afluencia
            conn.execute("""
                CREATE VIEW IF NOT EXISTS vw_ranking_dias AS
                SELECT
                    dia_semana,
                    CASE dia_semana
                        WHEN 0 THEN 'Lunes'
                        WHEN 1 THEN 'Martes'
                        WHEN 2 THEN 'Miércoles'
                        WHEN 3 THEN 'Jueves'
                        WHEN 4 THEN 'Viernes'
                        WHEN 5 THEN 'Sábado'
                        WHEN 6 THEN 'Domingo'
                    END AS nombre_dia,
                    SUM(cantidad)          AS total_visitantes,
                    COUNT(*)               AS total_visitas,
                    ROUND(AVG(cantidad), 2) AS promedio_visitantes
                FROM visitas_historico
                GROUP BY dia_semana
                ORDER BY total_visitantes DESC
            """)

            # ── VISTA 3: ocupación promedio por categoría ─────────────
            # Stored procedure: % ocupación por tipo de destino
            conn.execute("""
                CREATE VIEW IF NOT EXISTS vw_ocupacion_categoria AS
                SELECT
                    categoria,
                    COUNT(DISTINCT destino_id)          AS num_destinos,
                    SUM(cantidad)                        AS total_visitantes,
                    COUNT(*)                             AS total_visitas,
                    ROUND(
                        AVG(CAST(cantidad AS REAL) /
                            NULLIF(capacidad_max, 0) * 100
                        ), 2
                    ) AS ocupacion_promedio_pct
                FROM visitas_historico
                GROUP BY categoria
                ORDER BY ocupacion_promedio_pct DESC
            """)

            conn.commit()
            print("✅ SQLite inicializado — tablas, triggers y vistas (stored procedures) creados")
            print(f"   📂 Base de datos: {_DB_PATH}")

        finally:
            conn.close()

    # ── INSERCIÓN ─────────────────────────────────────────────────────

    def registrar_visita(self, destino_id: str, destino_nombre: str,
                          categoria: str, capacidad_max: int,
                          perfil_id: str, cantidad: int, fecha: str) -> None:
        """
        Inserta una visita en el historial SQL.
        El trigger trg_actualizar_resumen actualiza resumen_destino automáticamente.
        """
        try:
            dt = datetime.fromisoformat(fecha.replace('Z', '+00:00'))
        except Exception:
            dt = datetime.now(timezone.utc)

        conn = _get_conn()
        try:
            conn.execute("""
                INSERT INTO visitas_historico
                    (destino_id, destino_nombre, categoria, capacidad_max,
                     perfil_id, cantidad, fecha, dia_semana, mes, anio)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                destino_id, destino_nombre, categoria, capacidad_max,
                perfil_id, cantidad, fecha,
                dt.weekday(), dt.month, dt.year
            ))
            conn.commit()
        finally:
            conn.close()

    # ── STORED PROCEDURES ─────────────────────────────────────────────

    def sp_afluencia_por_destino(self) -> list:
        """
        SP: resumen de afluencia total por destino.
        Lee desde la tabla resumen_destino (mantenida por el trigger).
        """
        conn = _get_conn()
        try:
            rows = conn.execute("""
                SELECT
                    destino_id,
                    destino_nombre,
                    categoria,
                    capacidad_max,
                    total_visitas,
                    total_visitantes,
                    ultima_visita,
                    ROUND(
                        CAST(total_visitantes AS REAL) /
                        NULLIF(capacidad_max, 0) * 100, 1
                    ) AS ocupacion_historica_pct
                FROM resumen_destino
                ORDER BY total_visitantes DESC
            """).fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()

    def sp_afluencia_por_mes(self, destino_id: str = None) -> list:
        """
        SP: afluencia agrupada por mes usando la vista vw_afluencia_mensual.
        Filtro opcional por destino_id.
        """
        conn = _get_conn()
        try:
            if destino_id:
                rows = conn.execute("""
                    SELECT * FROM vw_afluencia_mensual
                    WHERE destino_id = ?
                    ORDER BY anio DESC, mes DESC
                    LIMIT 24
                """, (destino_id,)).fetchall()
            else:
                rows = conn.execute("""
                    SELECT
                        anio, mes,
                        SUM(total_visitantes) AS total_visitantes,
                        SUM(total_visitas)    AS total_visitas,
                        ROUND(AVG(promedio_por_visita), 2) AS promedio_por_visita
                    FROM vw_afluencia_mensual
                    GROUP BY anio, mes
                    ORDER BY anio DESC, mes DESC
                    LIMIT 24
                """).fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()

    def sp_ranking_dias_semana(self, destino_id: str = None) -> list:
        """
        SP: ranking de días de semana por afluencia usando vw_ranking_dias.
        """
        conn = _get_conn()
        try:
            if destino_id:
                rows = conn.execute("""
                    SELECT
                        dia_semana,
                        CASE dia_semana
                            WHEN 0 THEN 'Lunes'   WHEN 1 THEN 'Martes'
                            WHEN 2 THEN 'Miércoles' WHEN 3 THEN 'Jueves'
                            WHEN 4 THEN 'Viernes' WHEN 5 THEN 'Sábado'
                            WHEN 6 THEN 'Domingo'
                        END AS nombre_dia,
                        SUM(cantidad)           AS total_visitantes,
                        COUNT(*)                AS total_visitas,
                        ROUND(AVG(cantidad), 2) AS promedio_visitantes
                    FROM visitas_historico
                    WHERE destino_id = ?
                    GROUP BY dia_semana
                    ORDER BY total_visitantes DESC
                """, (destino_id,)).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM vw_ranking_dias"
                ).fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()

    def sp_ocupacion_promedio_categoria(self) -> list:
        """
        SP: % de ocupación promedio por categoría usando vw_ocupacion_categoria.
        """
        conn = _get_conn()
        try:
            rows = conn.execute(
                "SELECT * FROM vw_ocupacion_categoria"
            ).fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()

    def sp_historial_visitas(self, destino_id: str = None,
                              limit: int = 50) -> list:
        """
        SP: historial de visitas recientes con detalle completo.
        """
        conn = _get_conn()
        try:
            if destino_id:
                rows = conn.execute("""
                    SELECT
                        id, destino_id, destino_nombre, categoria,
                        perfil_id, cantidad, fecha,
                        CASE dia_semana
                            WHEN 0 THEN 'Lunes'   WHEN 1 THEN 'Martes'
                            WHEN 2 THEN 'Miércoles' WHEN 3 THEN 'Jueves'
                            WHEN 4 THEN 'Viernes' WHEN 5 THEN 'Sábado'
                            WHEN 6 THEN 'Domingo'
                        END AS nombre_dia,
                        mes, anio
                    FROM visitas_historico
                    WHERE destino_id = ?
                    ORDER BY fecha DESC
                    LIMIT ?
                """, (destino_id, limit)).fetchall()
            else:
                rows = conn.execute("""
                    SELECT
                        id, destino_id, destino_nombre, categoria,
                        perfil_id, cantidad, fecha,
                        CASE dia_semana
                            WHEN 0 THEN 'Lunes'   WHEN 1 THEN 'Martes'
                            WHEN 2 THEN 'Miércoles' WHEN 3 THEN 'Jueves'
                            WHEN 4 THEN 'Viernes' WHEN 5 THEN 'Sábado'
                            WHEN 6 THEN 'Domingo'
                        END AS nombre_dia,
                        mes, anio
                    FROM visitas_historico
                    ORDER BY fecha DESC
                    LIMIT ?
                """, (limit,)).fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()
