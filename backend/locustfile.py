"""
locustfile.py
Pruebas de rendimiento — Sistema Turismo Sostenible Junín
Herramienta: Locust (https://locust.io)

Simula usuarios concurrentes accediendo a los 4 endpoints principales:
  - GET  /destinos                    → listar destinos
  - POST /destinos/:id/visita         → registrar visita
  - GET  /prediccion/:id              → predicción ML
  - GET  /reportes/afluencia-destinos → reporte SQLite

USO:
  pip install locust
  locust -f locustfile.py --host=http://localhost:5000

Luego abrir: http://localhost:8089
  - Number of users   → 500 (o 1000)
  - Spawn rate        → 10 (usuarios nuevos por segundo)
  - Host              → http://localhost:5000
"""

import random
from locust import HttpUser, task, between, events

# ─────────────────────────────────────────────────────────────────
# IDs de destinos reales (los que carga seed_data.py en Firestore)
# Si los IDs en tu Firestore son distintos, cámbialos aquí.
# Puedes verlos haciendo GET http://localhost:5000/destinos
# ─────────────────────────────────────────────────────────────────
DESTINOS_IDS = [
    "abHvMcdRB0dR8DmTlIVD",  # Convento de Ocopa
    "JtAXXoJZpsxLJ2olaaqh",  # Gruta de Huagapo
    "vbtAMbcNIjaHuN9iyrOo",  # Laguna de Paca
    "jbvXk2cqvFbC4DAwb4NC",  # Nevado Huaytapallana
    "mcrJl2YhUzUX4HAAV0zg",  # Reserva de Junín
    "DBuL6497MLg0PmXxCBXb",  # Valle del Perené
]

PERFILES_IDS = [
    "perfil-test-01",
    "perfil-test-02",
    "perfil-test-03",
]


class UsuarioTurista(HttpUser):
    """
    Simula un turista que:
      - Consulta la lista de destinos (acción más frecuente)
      - Ve la predicción de afluencia antes de visitar
      - Registra su visita
      - Consulta reportes generales
    """

    # Tiempo de espera entre cada acción (simula comportamiento humano)
    wait_time = between(1, 3)

    # ── Endpoint 1: Listar destinos ───────────────────────────────
    @task(4)  # peso 4 → más frecuente (40% de las solicitudes)
    def listar_destinos(self):
        with self.client.get(
            "/destinos",
            name="GET /destinos",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Status inesperado: {response.status_code}")

    # ── Endpoint 1b: Listar por categoría ────────────────────────
    @task(2)  # peso 2 → frecuencia media
    def listar_destinos_por_categoria(self):
        categoria = random.choice(["Natural", "Cultural", "Histórico"])
        with self.client.get(
            f"/destinos?categoria={categoria}",
            name="GET /destinos?categoria=",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Status inesperado: {response.status_code}")

    # ── Endpoint 2: Predicción ML ─────────────────────────────────
    @task(3)  # peso 3 → frecuencia media-alta
    def predecir_afluencia(self):
        destino_id = random.choice(DESTINOS_IDS)
        dia = random.randint(0, 6)
        mes = random.randint(1, 12)
        with self.client.get(
            f"/prediccion/{destino_id}?dia={dia}&mes={mes}",
            name="GET /prediccion/:id",
            catch_response=True
        ) as response:
            if response.status_code in (200, 404):
                # 404 es válido si el destino_id no existe en Firestore aún
                response.success()
            else:
                response.failure(f"Error ML: {response.status_code}")

    # ── Endpoint 3: Registrar visita ──────────────────────────────
    @task(2)  # peso 2 → menos frecuente (acción de escritura)
    def registrar_visita(self):
        destino_id = random.choice(DESTINOS_IDS)
        perfil_id  = random.choice(PERFILES_IDS)
        payload    = {"perfil_id": perfil_id, "cantidad": 1}
        with self.client.post(
            f"/destinos/{destino_id}/visita",
            json=payload,
            name="POST /destinos/:id/visita",
            catch_response=True
        ) as response:
            if response.status_code in (200, 400, 404):
                # 400 = capacidad llena (comportamiento esperado), 404 = ID no existe
                response.success()
            else:
                response.failure(f"Error visita: {response.status_code}")

    # ── Endpoint 4a: Reporte afluencia por destino (SQLite) ───────
    @task(2)
    def reporte_afluencia_destinos(self):
        with self.client.get(
            "/reportes/afluencia-destinos",
            name="GET /reportes/afluencia-destinos",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Error reporte: {response.status_code}")

    # ── Endpoint 4b: Reporte ranking de días (SQLite) ─────────────
    @task(1)
    def reporte_ranking_dias(self):
        with self.client.get(
            "/reportes/ranking-dias",
            name="GET /reportes/ranking-dias",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Error reporte: {response.status_code}")

    # ── Endpoint 4c: Reporte afluencia mensual (SQLite) ───────────
    @task(1)
    def reporte_afluencia_mensual(self):
        with self.client.get(
            "/reportes/afluencia-mensual",
            name="GET /reportes/afluencia-mensual",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Error reporte: {response.status_code}")

    # ── Health check ──────────────────────────────────────────────
    @task(1)
    def health_check(self):
        with self.client.get(
            "/health",
            name="GET /health",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure("Health check falló")


# ─────────────────────────────────────────────────────────────────
# Evento: imprime resumen cuando termina la prueba
# ─────────────────────────────────────────────────────────────────
@events.quitting.add_listener
def resumen_final(environment, **kwargs):
    stats = environment.runner.stats.total
    print("\n" + "="*60)
    print("  RESUMEN PRUEBA DE RENDIMIENTO — TURISMO JUNÍN")
    print("="*60)
    print(f"  Total solicitudes   : {stats.num_requests}")
    print(f"  Solicitudes fallidas: {stats.num_failures}")
    print(f"  Tiempo resp. medio  : {stats.avg_response_time:.0f} ms")
    print(f"  Tiempo resp. 95%    : {stats.get_response_time_percentile(0.95):.0f} ms")
    print(f"  Solicitudes/segundo : {stats.current_rps:.1f} RPS")
    print("="*60)
