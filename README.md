```markdown
# 🌿 Turismo Sostenible Junín — Sistema de Monitoreo

Sistema web para monitorear la afluencia turística en tiempo real en destinos de la región Junín, Perú. Genera alertas automáticas por capacidad y cuenta con un asistente de IA integrado.

---

## 🛠️ Tecnologías utilizadas

- **Backend:** Python 3 + Flask + Firebase Admin SDK
- **Base de datos:** Firebase Firestore (nube)
- **Frontend:** HTML5 + CSS3 + JavaScript vanilla
- **IA:** Groq API — Llama 3.3 70B (gratuito)

---

## 📋 Requisitos previos

Antes de instalar asegúrate de tener:

- Python 3.10 o superior instalado
- pip actualizado
- Archivo `firebase_credentials.json` dentro de `backend/config/`
- API key de Groq (obtenida en [console.groq.com](https://console.groq.com))

---

## 🚀 Instalación y ejecución

### 1. Clonar o descomprimir el proyecto

Si lo descargaste como ZIP, descomprímelo en la carpeta de tu preferencia.

```
turismo-firebase/
├── backend/
│   ├── app.py
│   ├── requirements.txt
│   ├── config/
│   │   ├── firebase_credentials.json  ← tus credenciales Firebase
│   │   ├── firebase_init.py
│   │   └── seed_data.py
│   ├── routes/
│   │   ├── destinos.py
│   │   ├── perfiles.py
│   │   └── alertas.py
│   └── error_handlers.py
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

### 2. Abrir una terminal y entrar a la carpeta del backend

```bash
cd turismo-firebase/backend
```

### 3. (Opcional pero recomendado) Crear un entorno virtual

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

Esto instalará automáticamente:
- `flask` — servidor web
- `flask-cors` — manejo de CORS para el frontend
- `firebase-admin` — conexión con Firestore

### 5. Ejecutar el backend

```bash
python app.py
```

Si todo está correcto verás en la terminal:

```
==================================================
🌿 SISTEMA TURISMO SOSTENIBLE - JUNÍN
==================================================
🔥 Base de datos: Firebase Firestore
🌐 URL: http://localhost:5000
==================================================
🌱 6 destinos iniciales cargados en Firestore.
```

> La primera vez que ejecutes el backend, los 6 destinos turísticos de Junín se cargarán automáticamente en Firestore. Las siguientes veces ese paso se omite.

### 6. Configurar el asistente IA (Wayra)

Abre el archivo `frontend/scripts/asistente.js` y en la línea 16 reemplaza la API key:

```javascript
const GROQ_API_KEY = 'gsk_xxxxxxxxxxxxxxxxxxxxxxxx';
```

### 7. Abrir el frontend

Con el backend corriendo, abre el archivo `frontend/index.html` directamente en tu navegador. No necesita servidor adicional.

---

## ✅ Verificar que todo funciona

| Componente | Cómo verificar |
|---|---|
| Backend activo | Ir a `http://localhost:5000/health` — debe mostrar `{"status": "ok"}` |
| Firestore conectado | Ver colección `destinos` en la consola de Firebase |
| Frontend cargado | Los 6 destinos aparecen en la página |
| Asistente IA | Hacer clic en el botón "Guía IA" en la esquina inferior derecha |

---

# 🔷 Arquitectura Hexagonal — Sistema de Turismo Sostenible Junín

## ¿Qué es la Arquitectura Hexagonal?

La **Arquitectura Hexagonal** (también llamada *Ports & Adapters*), propuesta por Alistair Cockburn, 
organiza el software en tres zonas concéntricas:

- **Dominio (núcleo):** contiene las entidades y reglas de negocio puras, sin depender de ningún framework.
- **Aplicación:** contiene los casos de uso que orquestan el flujo de información entre el dominio y el exterior.
- **Infraestructura:** contiene los adaptadores que conectan el sistema con el mundo exterior (base de datos, API REST, IA, etc.).

La comunicación entre zonas se realiza exclusivamente a través de **puertos** (interfaces/contratos).

---

## 🗂️ Estructura de carpetas del proyecto

```
Turismo-Junin_V4/
│
├── backend/                            ← Núcleo del sistema
│   │
│   ├── domain/                         ← CAPA DE DOMINIO (núcleo puro)
│   │   ├── entities/                   ← Entidades del negocio
│   │   │   └── README.md               ← Destino, Perfil, Alerta, Visita
│   │   └── ports/                      ← Puertos (contratos/interfaces)
│   │       ├── input/                  ← Puertos de entrada (lo que el exterior puede pedir)
│   │       │   └── README.md
│   │       └── output/                 ← Puertos de salida (lo que el dominio necesita del exterior)
│   │           └── README.md
│   │
│   ├── application/                    ← CAPA DE APLICACIÓN (casos de uso)
│   │   └── use_cases/                  ← Orquestadores de lógica de negocio
│   │       └── README.md
│   │
│   ├── infrastructure/                 ← CAPA DE INFRAESTRUCTURA (adaptadores)
│   │   └── adapters/
│   │       ├── input/
│   │       │   └── api/                ← Adaptador de entrada: API REST (Flask)
│   │       │       └── README.md       ← routes/destinos.py, perfiles.py, alertas.py
│   │       └── output/
│   │           └── database/           ← Adaptador de salida: Firebase Firestore
│   │               └── README.md       ← config/firebase_init.py, seed_data.py
│   │
│   ├── routes/                         ← Implementación: Adaptadores de entrada REST
│   │   ├── destinos.py                 → mapea a infrastructure/adapters/input/api
│   │   ├── perfiles.py                 → mapea a infrastructure/adapters/input/api
│   │   └── alertas.py                  → mapea a infrastructure/adapters/input/api
│   │
│   ├── models/                         ← Implementación: Entidades del dominio
│   │   └── __init__.py                 → mapea a domain/entities
│   │
│   ├── config/                         ← Implementación: Adaptadores de salida (BD)
│   │   ├── firebase_init.py            → mapea a infrastructure/adapters/output/database
│   │   └── seed_data.py                → mapea a infrastructure/adapters/output/database
│   │
│   ├── app.py                          ← Punto de entrada (bootstrap de la aplicación)
│   └── error_handlers.py               ← Manejo transversal de errores
│
└── frontend/                           ← ADAPTADOR DE ENTRADA: Interfaz de usuario
    ├── index.html                      → UI principal (puerto de entrada visual)
    ├── styles.css
    └── scripts/
        ├── api.js                      → Cliente HTTP (adaptador hacia la API REST)
        ├── asistente.js                → Adaptador externo: Groq API / IA (Wayra)
        ├── destinos.js                 → Lógica de presentación de destinos
        ├── perfiles.js                 → Lógica de presentación de perfiles
        ├── alertas.js                  → Lógica de presentación de alertas
        ├── config.js                   → Configuración del adaptador frontend
        ├── utils.js                    → Utilidades transversales
        └── init.js                     → Inicialización del frontend
```

---

## 🔷 Diagrama de la Arquitectura Hexagonal

```
                        ┌─────────────────────────────────┐
                        │         ADAPTADORES              │
                        │         DE ENTRADA               │
                        │                                  │
                        │  ┌──────────┐  ┌─────────────┐  │
                        │  │ Frontend │  │  API REST   │  │
                        │  │(HTML/JS) │  │   (Flask)   │  │
                        │  └────┬─────┘  └──────┬──────┘  │
                        │       │               │          │
                        └───────┼───────────────┼──────────┘
                                │    PUERTOS    │
                                │    ENTRADA    │
                         ┌──────▼───────────────▼──────┐
                         │                              │
                         │    CAPA DE APLICACIÓN        │
                         │      (Casos de Uso)          │
                         │  registrar_visita()          │
                         │  generar_alerta()            │
                         │  gestionar_perfil()          │
                         │                              │
                         │   ┌──────────────────────┐   │
                         │   │    DOMINIO (núcleo)   │   │
                         │   │                       │   │
                         │   │  Entidades:           │   │
                         │   │  • Destino            │   │
                         │   │  • Perfil             │   │
                         │   │  • Alerta             │   │
                         │   │  • Visita             │   │
                         │   │                       │   │
                         │   │  Reglas de negocio:   │   │
                         │   │  • % ocupación        │   │
                         │   │  • Estado (semáforo)  │   │
                         │   │  • Sin duplicar alerta│   │
                         │   └──────────────────────┘   │
                         │                              │
                         └──────────────┬───────────────┘
                                        │
                                  PUERTOS SALIDA
                                        │
                        ┌───────────────▼──────────────────┐
                        │       ADAPTADORES DE SALIDA       │
                        │                                   │
                        │  ┌──────────────┐  ┌───────────┐  │
                        │  │   Firebase   │  │ Groq API  │  │
                        │  │  Firestore   │  │ (Llama3.3)│  │
                        │  └──────────────┘  └───────────┘  │
                        │                                   │
                        └───────────────────────────────────┘
```

---

## 📌 Mapeo componente → capa hexagonal

| Archivo / Componente            | Capa Hexagonal              | Rol                                      |
|---------------------------------|-----------------------------|------------------------------------------|
| `routes/destinos.py`            | Adaptador de Entrada        | Expone endpoints REST de destinos        |
| `routes/perfiles.py`            | Adaptador de Entrada        | Expone endpoints REST de perfiles        |
| `routes/alertas.py`             | Adaptador de Entrada        | Expone endpoints REST de alertas         |
| `config/firebase_init.py`       | Adaptador de Salida         | Conexión con Firebase Firestore          |
| `config/seed_data.py`           | Adaptador de Salida         | Carga inicial de datos en BD             |
| `models/__init__.py`            | Dominio — Entidades         | Definición de entidades del negocio      |
| `backend/app.py`                | Bootstrap / Infraestructura | Inicializa y conecta todos los adaptadores|
| `frontend/scripts/api.js`       | Adaptador de Entrada (UI)   | Cliente HTTP que consume la API REST     |
| `frontend/scripts/asistente.js` | Adaptador de Salida (ext.)  | Conexión con Groq API (IA Wayra)         |
| `frontend/index.html`           | Adaptador de Entrada (UI)   | Interfaz visual del usuario              |
| `error_handlers.py`             | Transversal                 | Manejo de errores en todos los adaptadores|

---

## 🔄 Estados de afluencia

| Estado | Ocupación | Significado |
|---|---|---|
| 🟢 Bajo | < 40% | Disponible, ideal para visitar |
| 🟡 Moderado | 40 – 69% | Afluencia normal |
| 🟠 Alto | 70 – 89% | Alta afluencia, visitar temprano |
| 🔴 Crítico | ≥ 90% | Capacidad máxima, se recomienda no visitar |

---

## 🔒 Seguridad

- El archivo `firebase_credentials.json`. Está protegido en el `.gitignore`.
- La API key de Groq tampoco se esta compartiendo publicamente en este github.

---

## 👤 Autores

Michael Tovar   —    Ingeniería de Sistemas e Informática  
Jair Felix      —    Ingeniería de Sistemas e Informática
Frank Yupanqui  —    Ingeniería de Sistemas e Informática
Henry Arroyo    —    Ingeniería de Sistemas e Informática
--------------------------------------------
Universidad Continental · Junín, Perú · 2026
```