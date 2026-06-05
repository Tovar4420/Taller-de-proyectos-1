# Adaptador de Entrada — API REST (Flask)

Este es el **adaptador de entrada principal** del sistema.
Traduce las peticiones HTTP del mundo exterior en llamadas a los puertos de entrada del dominio.

## Archivos que implementan este adaptador

| Archivo                    | Puerto de entrada que implementa  | Endpoints expuestos                        |
|----------------------------|-----------------------------------|--------------------------------------------|
| `backend/routes/destinos.py` | Puerto: Gestión de Destinos     | GET /destinos, GET /destinos/:id, POST /destinos/:id/visita, POST /destinos/:id/salida, GET /health |
| `backend/routes/perfiles.py` | Puerto: Gestión de Perfiles     | GET /perfiles, POST /perfiles, GET /perfiles/:id, DELETE /perfiles/:id |
| `backend/routes/alertas.py`  | Puerto: Gestión de Alertas      | GET /alertas, DELETE /alertas/:id          |

## Tecnología
- **Framework:** Flask 3.0.3 con Blueprints
- **CORS:** flask-cors 4.0.1 (permite llamadas desde el frontend)
- **Formato de datos:** JSON

## Flujo de una petición HTTP

```
Navegador / Frontend
       │
       ▼  HTTP Request (JSON)
  Flask Router (app.py)
       │
       ▼
  Blueprint (routes/*.py)   ← Este adaptador
       │  valida, parsea y transforma
       ▼
  Lógica de negocio (dominio)
       │
       ▼
  Firebase Firestore (adaptador de salida)
       │
       ▼  HTTP Response (JSON)
  Navegador / Frontend
```
