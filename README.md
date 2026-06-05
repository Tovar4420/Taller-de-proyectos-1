# 🌿 Turismo Sostenible Junín — Sistema de Monitoreo

Sistema web para monitorear la afluencia turística en tiempo real en destinos de la región Junín, Perú.
Registra visitas, genera alertas automáticas por capacidad, predice la afluencia futura mediante
Machine Learning (Random Forest) y cuenta con un asistente de IA integrado.

---

## 🛠️ Tecnologías utilizadas

| Capa                  | Tecnología                                                    |
|---                    |---                                                            |
| Backend               | Python 3.10+ · Flask 3.0 · Firebase Admin SDK                 |
| Base de datos (RT)    | Firebase Firestore (tiempo real, operacional)                 |
| Base de datos (SQL)   | SQLite — historial analítico con Stored Procedures            |
| Machine Learning      | scikit-learn — Random Forest Regressor · NumPy                |
| Frontend              | HTML5 · CSS3 · JavaScript vanilla                             |
| Asistente IA          | Groq API — Llama 3.3 70B                                      |

---

## 📋 Requisitos previos

Antes de instalar asegúrate de tener:

- Python 3.10 o superior instalado
- `pip` actualizado
- Archivo `firebase_credentials.json` dentro de `backend/config/`
- API key de Groq (obtenida en [console.groq.com](https://console.groq.com))

---

## 🚀 Instalación y ejecución

### 1. Descomprimir el proyecto

```
turismo-refactored/
├── backend/
│   ├── app.py
│   ├── requirements.txt
│   ├── error_handlers.py
│   ├── config/
│   │   ├── firebase_credentials.json  ← tus credenciales Firebase
│   │   ├── firebase_init.py
│   │   └── seed_data.py
│   ├── domain/
│   │   ├── entities/
│   │   └── ports/
│   │       ├── input/
│   │       └── output/
│   ├── application/
│   │   └── use_cases/
│   ├── infrastructure/
│   │   └── adapters/
│   │       ├── input/api/
│   │       └── output/
│   │           ├── database/
│   │           └── ml/
│   └── routes/
│       ├── destinos.py
│       ├── perfiles.py
│       ├── alertas.py
│       └── prediccion.py
└── frontend/
    ├── index.html
    ├── styles.css
    └── scripts/
        ├── config.js
        ├── api.js
        ├── destinos.js
        ├── perfil.js
        ├── alertas.js
        ├── asistente.js  ← configurar API key de Groq aquí
        ├── utils.js
        └── init.js
```

### 2. Entrar a la carpeta del backend

```bash
cd turismo-refactored/backend
```

### 3. (Recomendado) Crear un entorno virtual

```bash
# Crear entorno virtual
python -m venv venv

# Activar en Windows
venv\Scripts\activate

# Activar en Mac/Linux
source venv/bin/activate
```

### 4. Instalar las dependencias

```bash
pip install -r requirements.txt
```

Dependencias incluidas en `requirements.txt`:

```
flask==3.0.3
flask-cors==4.0.1
firebase-admin==6.5.0
scikit-learn==1.5.2
numpy==2.1.3
```

### 5. Ejecutar el backend

```bash
python app.py
```

Si todo está correcto verás en la terminal:

```
============================================================
🌿 SISTEMA TURISMO SOSTENIBLE - JUNÍN
============================================================
🔥 Base de datos : Firebase Firestore (tiempo real)
🗄️  Reportes SQL  : SQLite + Stored Procedures
🤖 ML            : Random Forest Regressor
🌐 URL           : http://localhost:5000
============================================================
✅ SQLite inicializado — tablas, triggers y vistas creados
   📂 Base de datos: backend/turismo_historico.db
============================================================
```

> La primera vez que ejecutes el backend, los 6 destinos turísticos de Junín
> se cargarán automáticamente en Firestore. Las siguientes veces ese paso se omite.

### 6. Configurar el asistente IA (Wayra)

Abre `frontend/scripts/asistente.js` y reemplaza la API key de Groq:

```javascript
const GROQ_API_KEY = 'gsk_xxxxxxxxxxxxxxxxxxxxxxxx';
```

### 7. Abrir el frontend

Con el backend corriendo, abre `frontend/index.html` directamente en el navegador.
No necesita servidor adicional.

---

## ✅ Verificar que todo funciona

| Componente          | Cómo verificar                                                        |
|---                  |---                                                                    |
| Backend activo      | Ir a `http://localhost:5000/health` → debe mostrar `{"status": "ok"}` |
| Firestore conectado | Ver colección `destinos` en la consola de Firebase                    |
| Frontend cargado    | Los 6 destinos aparecen en la página                                  |
| Predicción ML       | Llamar a `GET /prediccion/<id>` — debe retornar `porcentaje_predicho` |
| SQLite inicializado | Ver mensaje `✅ SQLite inicializado` en consola al arrancar           | 
| Stored Procedures   | Llamar a `GET /reportes/afluencia-destinos` — retorna datos SQL       |
| Asistente IA        | Clic en "Guía IA" (esquina inferior derecha)                          |

---

## 📡 Endpoints de la API REST

| Método    | Ruta                           | Descripción                                             |
|---        |---                             |---                                                      |
| `GET`     | `/destinos`                    | Listar destinos (filtro opcional: `?categoria=Natural`) |
| `GET`     | `/destinos/:id`                | Obtener un destino por ID                               |
| `POST`    | `/destinos/:id/visita`         | Registrar entrada de visitantes                         |
| `POST`    | `/destinos/:id/salida`         | Registrar salida de visitantes                          |
| `GET`     | `/perfiles`                    | Listar perfiles de usuario                              |
| `POST`    | `/perfiles`                    | Crear un nuevo perfil                                   |
| `GET`     | `/perfiles/:id`                | Obtener un perfil por ID                                |
| `DELETE`  | `/perfiles/:id`                | Eliminar un perfil                                      |
| `GET`     | `/alertas`                     | Ver alertas activas                                     |
| `DELETE`  | `/alertas/:id`                 | Resolver (desactivar) una alerta                        |
| `GET`     | `/prediccion/:id`              | Predecir afluencia ML para un destino                   |
| `GET`     | `/prediccion/metricas`         | Métricas de rendimiento del modelo                      |
| `POST`    | `/prediccion/entrenar`         | Reentrenar el modelo con datos de Firestore             |
| `GET`     | `/prediccion/datos-bd`         | Resumen de datos usados para entrenar                   |
| `GET`     | `/prediccion/:id/mejores-dias` | **ML Caso 2:** ranking de mejores días para visitar     |
| `GET`     | `/health`                      | Estado del servidor                                     |

### 📊 Endpoints SQLite — Stored Procedures

| Método | Ruta                               | Stored Procedure           | Descripción                                |
|---     |---                                 |---                         |---                                         |
| `GET`  | `/reportes/afluencia-destinos`     | `sp_afluencia_por_destino` | Resumen total de afluencia por destino     |
| `GET`  | `/reportes/afluencia-mensual`      | `vw_afluencia_mensual`     | Afluencia agrupada por mes y año           |
| `GET`  | `/reportes/ranking-dias`           | `vw_ranking_dias`          | Ranking de días de semana por afluencia    |
| `GET`  | `/reportes/ocupacion-categoria`    | `vw_ocupacion_categoria`   | % de ocupación promedio por categoría      |
| `GET`  | `/reportes/historial`              | `sp_historial_visitas`     | Historial detallado de visitas             |

> Parámetros opcionales: `?destino_id=<id>` para filtrar por destino · `?limit=<n>` para limitar resultados.

---

# 🔷 Arquitectura Hexagonal — Ports & Adapters

## ¿Qué es la Arquitectura Hexagonal?

La **Arquitectura Hexagonal** (*Ports & Adapters*), propuesta por Alistair Cockburn,
organiza el software en tres zonas concéntricas con una regla fundamental:
**las dependencias solo apuntan hacia adentro**. El dominio no conoce Flask, Firestore
ni scikit-learn.

| Zona                | Responsabilidad                                                        |
|---                  |---                                                                     |
| **Dominio**         | Entidades y reglas de negocio puras. Sin imports externos.             |
| **Aplicación**      | Casos de uso que orquestan el dominio. Implementan puertos de entrada. |
| **Infraestructura** | Adaptadores que conectan con el mundo exterior (BD, ML, HTTP).         |

La comunicación entre zonas se realiza exclusivamente a través de **puertos** (clases abstractas ABC).

---

## 🗂️ Estructura de carpetas del proyecto

```
turismo-refactored/
├── backend/
│   ├── app.py                                          ← Bootstrap: registra blueprints e inicializa Firebase
│   ├── requirements.txt                                ← Dependencias Python
│   ├── error_handlers.py                               ← Manejadores de error HTTP globales
│   │
│   ├── domain/                                         ← ① NÚCLEO — sin dependencias externas
│   │   ├── entities/
│   │   │   └── __init__.py                             ← Entidades: Destino, Perfil, Alerta
│   │   └── ports/
│   │       ├── input/
│   │       │   └── __init__.py                         ← Puertos de entrada: DestinoServicePort,
│   │       │                                               AlertaServicePort, PerfilServicePort,
│   │       │                                               PrediccionServicePort
│   │       └── output/
│   │           └── __init__.py                         ← Puertos de salida: DestinoRepositoryPort,
│   │                                                       AlertaRepositoryPort, PerfilRepositoryPort,
│   │                                                       PrediccionRepositoryPort, VisitaRepositoryPort,
│   │                                                       ReporteRepositoryPort
│   │
│   ├── application/                                    ← ② APLICACIÓN — orquestación
│   │   └── use_cases/
│   │       └── __init__.py                             ← DestinoUseCase, AlertaUseCase,
│   │                                                       PerfilUseCase, PrediccionUseCase,
│   │                                                       ReporteUseCase
│   │
│   ├── infrastructure/                                 ← ③ INFRAESTRUCTURA — tecnologías concretas
│   │   └── adapters/
│   │       ├── input/
│   │       │   └── api/
│   │       │       └── __init__.py                     ← (reservado para adaptadores HTTP adicionales)
│   │       └── output/
│   │           ├── database/
│   │           │   ├── __init__.py                     ← FirestoreDestinoRepository,
│   │           │   │                                       FirestoreAlertaRepository,
│   │           │   │                                       FirestorePerfilRepository,
│   │           │   │                                       FirestoreVisitaRepository
│   │           │   └── sqlite_repository.py            ← SQLiteReporteRepository
│   │           │                                           (Stored Procedures, Triggers, Vistas)
│   │           └── ml/
│   │               └── __init__.py                     ← RandomForestPrediccionAdapter
│   │
│   ├── routes/                                         ← Adaptadores de entrada HTTP (Flask Blueprints)
│   │   ├── destinos.py                                 ← Endpoints /destinos
│   │   ├── perfiles.py                                 ← Endpoints /perfiles
│   │   ├── alertas.py                                  ← Endpoints /alertas
│   │   └── prediccion.py                               ← Endpoints /prediccion
│   │
│   └── config/
│       ├── firebase_init.py                            ← Conexión con Firebase
│       ├── firebase_credentials.json                   ← Credenciales Firebase (en .gitignore)
│       └── seed_data.py                                ← Carga inicial de los 6 destinos
│
└── frontend/
    ├── index.html                                      ← Página principal
    ├── styles.css                                      ← Estilos (verde naturaleza + dorado)
    └── scripts/
        ├── config.js                                   ← Estado global y configuración
        ├── api.js                                      ← Cliente HTTP hacia el backend
        ├── destinos.js                                 ← Lógica de destinos y predicción ML
        ├── perfil.js                                   ← Gestión de perfiles
        ├── alertas.js                                  ← Panel de alertas
        ├── asistente.js                                ← Asistente IA Wayra (Groq API)
        ├── utils.js                                    ← Utilidades y auto-refresh
        └── init.js                                     ← Inicialización de la app
```

---

## 🔄 Flujo de una solicitud HTTP a través del hexágono

```
  USUARIO / FRONTEND
        │
        │  HTTP Request
        ▼
  ┌─────────────┐
  │  routes/    │  Adaptador de entrada — solo traduce HTTP → caso de uso
  │  (Flask BP) │  No contiene lógica de negocio
  └──────┬──────┘
         │  llama a método del puerto de entrada
         ▼
  ┌────────────────────────┐
  │  application/          │  Caso de uso — orquesta el flujo
  │  use_cases/            │  Implementa el puerto de entrada (ABC)
  │                        │  Usa puertos de salida para persistir
  │  ┌──────────────────┐  │
  │  │  domain/         │  │  Núcleo — reglas de negocio puras
  │  │  entities/       │  │  Destino.puede_recibir()
  │  │                  │  │  Destino.tipo_alerta_necesaria()
  │  └──────────────────┘  │  Destino.porcentaje_ocupacion
  └──────────┬─────────────┘
             │  a través de puerto de salida (ABC)
             ▼
  ┌──────────────────────────────────────────────┐
  │  infrastructure/adapters/output/             │  Adaptadores de salida
  │                                              │
  │  database/__init__.py  →  Firebase Firestore │  Tiempo real / operacional
  │  database/sqlite_repo  →  SQLite + SPs       │  Historial analítico SQL
  │  ml/                   →  Random Forest      │  Intercambiable por XGBoost
  └──────────────────────────────────────────────┘
```

---

## 🔷 Diagrama de la Arquitectura Hexagonal

```
                ┌───────────────────────────────────────────┐
                │           ADAPTADORES DE ENTRADA          │
                │                                           │
                │   ┌───────────────┐   ┌─────────────────┐ │
                │   │   Frontend    │   │  routes/ HTTP   │ │
                │   │  (HTML/JS)    │   │ Flask Blueprints│ │
                │   └──────┬────────┘   └───────┬─────────┘ │
                └──────────┼────────────────────┼───────────┘
                           │   PUERTOS ENTRADA  │
                           │  (ServicePort ABC) │
                    ┌──────▼────────────────────▼────────┐
                    │        CAPA DE APLICACIÓN          │
                    │          (Casos de Uso)            │
                    │                                    │
                    │  DestinoUseCase                    │
                    │  AlertaUseCase                     │
                    │  PerfilUseCase                     │
                    │  PrediccionUseCase                 │
                    │  ReporteUseCase                    │
                    │                                    │
                    │   ┌────────────────────────────┐   │
                    │   │      DOMINIO (núcleo)      │   │
                    │   │                            │   │
                    │   │  Entidades:                │   │
                    │   │  · Destino                 │   │
                    │   │  · Perfil                  │   │
                    │   │  · Alerta                  │   │
                    │   │                            │   │
                    │   │  Reglas de negocio:        │   │
                    │   │  · % de ocupación          │   │
                    │   │  · Estado semáforo         │   │
                    │   │  · Verificar capacidad     │   │
                    │   │  · Deduplicar alertas      │   │
                    │   │                            │   │
                    │   │  Puertos (contratos ABC):  │   │
                    │   │  · DestinoServicePort      │   │
                    │   │  · PerfilServicePort       │   │
                    │   │  · AlertaServicePort       │   │
                    │   │  · PrediccionServicePort   │   │
                    │   │  · DestinoRepositoryPort   │   │
                    │   │  · AlertaRepositoryPort    │   │
                    │   │  · PerfilRepositoryPort    │   │
                    │   │  · PrediccionRepositoryPort│   │
                    │   │  · VisitaRepositoryPort    │   │
                    │   │  · ReporteRepositoryPort   │   │
                    │   └────────────────────────────┘   │
                    └──────────────┬─────────────────────┘
                                   │  PUERTOS SALIDA
                                   │  (RepositoryPort ABC)
                ┌──────────────────▼────────────────────────────────┐
                │          ADAPTADORES DE SALIDA                    │
                │                                                   │
                │  ┌──────────────┐ ┌──────────────┐ ┌───────────┐  │
                │  │   Firebase   │ │    SQLite    │ │  Random   │  │
                │  │  Firestore   │ │  + Stored    │ │  Forest   │  │
                │  │              │ │  Procedures  │ │(sklearn)  │  │
                │  │ Firestore-   │ │              │ │           │  │
                │  │ DestinoRepo  │ │ SQLiteReporte│ │ Random-   │  │
                │  │ AlertaRepo   │ │ Repository   │ │ Forest-   │  │
                │  │ PerfilRepo   │ │  · Trigger   │ │ Prediccion│  │
                │  │ VisitaRepo   │ │  · 3 Vistas  │ │ Adapter   │  │
                │  └──────────────┘ │  · 5 SPs     │ └───────────┘  │
                │                   └──────────────┘                │
                └───────────────────────────────────────────────────┘
```

> **Nota:** El asistente IA Wayra (Groq API) se conecta directamente desde el
> frontend (`asistente.js`) y **no** forma parte del backend Python.

---

## 📌 Mapeo componente → capa hexagonal

| Archivo / Componente                                           | Capa Hexagonal               | Rol                                                                     |
|---                                                             |---                           |---                                                                      |
| `domain/entities/__init__.py`                                  | Dominio — Entidades          | `Destino`, `Perfil`, `Alerta` con reglas de negocio                     |
| `domain/ports/input/__init__.py`                               | Dominio — Puertos de entrada | Contratos `*ServicePort` (ABC)                                          |
| `domain/ports/output/__init__.py`                              | Dominio — Puertos de salida  | Contratos `*RepositoryPort` (ABC)                                       |
| `application/use_cases/__init__.py`                            | Aplicación                   | `DestinoUseCase`, `AlertaUseCase`, `PerfilUseCase`, `PrediccionUseCase` |
| `infrastructure/adapters/output/database/__init__.py`          | Adaptador de salida — BD     | Implementaciones Firestore de todos los repositorios                    |
| `infrastructure/adapters/output/ml/__init__.py`                | Adaptador de salida — ML     | `RandomForestPrediccionAdapter` (scikit-learn)                          |
| `routes/destinos.py`                                           | Adaptador de entrada — HTTP  | Endpoints REST `/destinos`                                              |
| `routes/perfiles.py`                                           | Adaptador de entrada — HTTP  | Endpoints REST `/perfiles`                                              |
| `routes/alertas.py`                                            | Adaptador de entrada — HTTP  | Endpoints REST `/alertas`                                               |
| `routes/prediccion.py`                                         | Adaptador de entrada — HTTP  | Endpoints REST `/prediccion`                                            |
| `routes/reportes.py`                                           | Adaptador de entrada — HTTP  | Endpoints REST `/reportes` — expone Stored Procedures SQLite            |
| `infrastructure/adapters/output/database/sqlite_repository.py` | Adaptador de salida — SQL    | `SQLiteReporteRepository`: tablas, trigger, 3 vistas, 5 SPs             |
| `application/use_cases/__init__.py` → `ReporteUseCase`         | Aplicación                   | Orquesta los stored procedures del repositorio SQLite                   |
| `domain/ports/output/__init__.py` → `ReporteRepositoryPort`    | Dominio — Puerto de salida   | Contrato ABC para cualquier implementación SQL                          |
| `config/firebase_init.py`                                      | Infraestructura — Config     | Inicialización de la conexión Firebase                                  |
| `config/seed_data.py`                                          | Infraestructura — Config     | Carga inicial de los 6 destinos en Firestore                            |
| `app.py`                                                       | Bootstrap                    | Registra blueprints, inicializa Firebase, SQLite y seeds                |
| `error_handlers.py`                                            | Transversal                  | Manejadores de error HTTP globales                                      |
| `frontend/scripts/api.js`                                      | Adaptador de entrada (UI)    | Cliente HTTP que consume la API REST                                    |
| `frontend/scripts/asistente.js`                                | Externo (frontend)           | Asistente IA Wayra vía Groq API                                         |
| `frontend/index.html`                                          | Adaptador de entrada (UI)    | Interfaz visual del usuario                                             |

---

## 🔄 Estados de afluencia

| Estado       | Ocupación | Color    | Significado                                 |
|---           |---        |---       |---                                          |
| 🟢 Bajo     | < 40%      | Verde    | Disponible, ideal para visitar             |  
| 🟡 Moderado | 40 – 69%   | Amarillo | Afluencia normal                           |
| 🟠 Alto     | 70 – 89%   | Naranja  | Alta afluencia, visitar temprano           |
| 🔴 Crítico  | ≥ 90%      | Rojo     | Capacidad máxima, no se recomienda visitar |

Las alertas se generan automáticamente al superar el **70 %** (advertencia) y el **90 %** (crítica),
sin duplicar alertas activas del mismo tipo para el mismo destino.


---

# 🗄️ Persistencia Dual: Firestore + SQLite

El sistema utiliza **dos motores de base de datos** con responsabilidades distintas:

| Característica     | Firebase Firestore                 | SQLite                                    |
|---                 |---                                 |---                                        |
| Tipo               | NoSQL (documentos)                 | SQL relacional                            |
| Propósito          | Datos operacionales en tiempo real | Historial analítico con queries complejas |
| Stored Procedures  | No soporta                         | Triggers, Vistas, funciones SQL           |
| Cuándo se escribe  | Cada visita registrada             | Dual-write simultáneo con Firestore       |
| Archivo generado   | Nube (Google Cloud)                | `backend/turismo_historico.db`            |

## Flujo Dual-Write

Al registrar una visita (`POST /destinos/:id/visita`), `DestinoUseCase` escribe en **ambas bases** de forma secuencial. Si SQLite falla, Firestore no se ve afectado (el error se captura y se loguea).

```
POST /destinos/:id/visita
        │
        ▼
DestinoUseCase.registrar_visita()
        │
        ├──→ FirestoreDestinoRepository   (tiempo real, visitantes actuales)
        │
        └──→ SQLiteReporteRepository      (historial analítico)
                    │
                    └──→ TRIGGER trg_actualizar_resumen
                              (actualiza resumen_destino automáticamente)
```

## Stored Procedures implementados en SQLite

| Nombre                            | Tipo SQL    | Descripción                                          |
|---                                |---          |---                                                   |
| `trg_actualizar_resumen`          | TRIGGER     | Actualiza totales en `resumen_destino` al insertar   |
| `vw_afluencia_mensual`            | VIEW        | Afluencia agrupada por destino, año y mes            |
| `vw_ranking_dias`                 | VIEW        | Días de semana ordenados por mayor afluencia         |
| `vw_ocupacion_categoria`          | VIEW        | % ocupación promedio por categoría (Natural, etc.)   |
| `sp_afluencia_por_destino`        | función SQL | Resumen total por destino desde `resumen_destino`    |
| `sp_afluencia_por_mes`            | función SQL | Filtra `vw_afluencia_mensual` por destino opcional   |
| `sp_ranking_dias_semana`          | función SQL | Filtra `vw_ranking_dias` por destino opcional        |
| `sp_ocupacion_promedio_categoria` | función SQL | Lee `vw_ocupacion_categoria`                         |
| `sp_historial_visitas`            | función SQL | Historial detallado con nombre de día en español     |

---

## 🤖 Modelo de Machine Learning

El adaptador `RandomForestPrediccionAdapter` entrena un **Random Forest Regressor** para predecir
el porcentaje de ocupación de un destino dado un día de la semana, mes, categoría y capacidad máxima.

## Casos de uso ML

| # | Endpoint                                | Descripción                                                             |
|---|---                                      |---                                                                      |
| 1 | `GET /prediccion/:id?dia=&mes=`         | Dado un día y mes, predice el % de ocupación del destino                |
| 2 | `GET /prediccion/:id/mejores-dias?mes=` | Para un mes dado, rankea los 7 días de menor a mayor ocupación predicha |

## Visualización en el frontend

Al abrir el modal de detalle de cualquier destino se muestran **ambos casos de uso ML** de forma simultánea:

```
Modal de detalle — Destino turístico
├── Nombre, categoría, estado semáforo
├── Descripción y ubicación
├── Barra de afluencia actual (tiempo real — Firestore)
│
├── 🤖 ML Caso 1 — Afluencia estimada hoy
│       Llama a GET /prediccion/:id?dia=&mes=
│       Muestra: % ocupación predicho, estado, recomendación, métricas R²
│
└── 📅 ML Caso 2 — Mejores días para visitar
        Llama a GET /prediccion/:id/mejores-dias?mes=
        Muestra: tabla ranking 7 días ordenados de menor a mayor ocupación
                 con barras de color semáforo y etiqueta "Mejor día"
```

**Variables de entrada del modelo:**

| Variable        | Tipo                           | Descripción                  |
|---              |---                             |---                           |
| `dia_semana`    | 0–6                            | Día (0 = lunes, 6 = domingo) |
| `mes`           | 1–12                           | Mes del año                  |
| `categoria`     | Natural / Cultural / Historico | Tipo de destino              |
| `capacidad_max` | entero                         | Aforo máximo del destino     |

**Estrategia de entrenamiento:**
- Si existen datos reales en Firestore, se ponderan y combinan con datos sintéticos.
- Si no hay datos reales, el modelo arranca con **900 registros sintéticos** calibrados con
  patrones de turismo de Junín (MINCETUR / CCT 2021).
- El modelo se entrena automáticamente en la primera predicción
  y puede reentrenarse con `POST /prediccion/entrenar`.

---

## 🔒 Seguridad

- `firebase_credentials.json` está protegido en `.gitignore` y nunca debe subirse al repositorio.
- La API key de Groq se configura localmente en `asistente.js` y tampoco se comparte públicamente.

---

## 👤 Autores

```
Michael Tovar   —   Ingeniería de Sistemas e Informática
Jair Felix      —   Ingeniería de Sistemas e Informática
Frank Yupanqui  —   Ingeniería de Sistemas e Informática
Henry Arroyo    —   Ingeniería de Sistemas e Informática
────────────────────────────────────────────────────────
Universidad Continental · Junín, Perú · 2026
```
