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
proyecto/
├── backend/
│   ├── app.py                                      ← Punto de entrada
│   ├── requirements.txt                            ← Dependencias Python
│   ├── error_handlers.py                           ← Manejadores de error globales
│   │
│   ├── domain/                                     ← NÚCLEO — lógica pura sin dependencias externas
│   │   ├── entities/
│   │   │   └── __init__.py                         ← Entidades: Destino, Perfil, Alerta
│   │   └── ports/
│   │       ├── input/
│   │       │   └── __init__.py                     ← Contratos de entrada (casos de uso expuestos)
│   │       └── output/
│   │           └── __init__.py                     ← Contratos de salida (repositorios)
│   │
│   ├── application/
│   │   └── use_cases/
│   │       └── __init__.py                         ← Casos de uso: DestinoUseCase, PerfilUseCase, AlertaUseCase
│   │
│   ├── infrastructure/                             ← INFRAESTRUCTURA — tecnologías concretas
│   │   └── adapters/
│   │       ├── input/
│   │       │   └── api/
│   │       │       └── __init__.py                 ← Adaptador de entrada HTTP (Flask)
│   │       └── output/
│   │           └── database/
│   │               └── __init__.py                 ← Adaptador de salida Firestore
│   │
│   ├── routes/                                     ← Controladores HTTP delgados (solo reciben requests)
│   │   ├── destinos.py
│   │   ├── perfiles.py
│   │   ├── alertas.py
│   │   └── prediccion.py
│   │
│   ├── services/
│   │   └── predictor_ml.py                         ← Modelo de Machine Learning (Random Forest)
│   │
│   └── config/
│       ├── firebase_init.py                        ← Conexión con Firebase
│       ├── firebase_credentials.json               ← Credenciales Firebase (privado)
│       └── seed_data.py                            ← Datos iniciales de destinos
│
└── frontend/
    ├── index.html                                  ← Página principal
    ├── styles.css                                  ← Estilos (verde naturaleza + dorado)
    └── scripts/
        ├── config.js                               ← Estado global y configuración
        ├── api.js                                  ← Comunicación con el backend
        ├── destinos.js                             ← Lógica de destinos y predicción ML
        ├── perfil.js                               ← Gestión de perfiles
        ├── alertas.js                              ← Panel de alertas
        ├── asistente.js                            ← Asistente IA Wayra (Groq)
        ├── utils.js                                ← Utilidades y auto-refresh
        └── init.js                                 ← Inicialización de la app
```

### Flujo de la arquitectura hexagonal

[Frontend / Asistente IA]           ← Adaptadores de entrada (usuarios)
          ↓
     [routes/]                      ← Reciben HTTP y delegan
          ↓
 [application/use_cases/]           ← Orquestan la lógica de negocio
          ↓
    [domain/entities/]              ← Reglas puras: estados, alertas, validaciones
          ↓
  [domain/ports/output/]            ← Contratos de repositorios
          ↓
[infrastructure/adapters/database/] ← Firestore (intercambiable)

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

| Estado        | Ocupación  | Significado                                  |
|---------------|------------|----------------------------------------------|
| 🟢 Bajo       | < 40%     | Disponible, ideal para visitar                |
| 🟡 Moderado   | 40 – 69%  | Afluencia normal                              |
| 🟠 Alto       | 70 – 89%  | Alta afluencia, visitar temprano              |
| 🔴 Crítico    | ≥ 90%     | Capacidad máxima, se recomienda no visitar    |

---

## 🔒 Seguridad

- El archivo `firebase_credentials.json`. Está protegido en el `.gitignore`.
- La API key de Groq tampoco se esta compartiendo publicamente en este github.

---

## 👤 Autores
```
Michael Tovar   —   Ingeniería de Sistemas e Informática  
Jair Felix      —   Ingeniería de Sistemas e Informática
Frank Yupanqui  —   Ingeniería de Sistemas e Informática
Henry Arroyo    —   Ingeniería de Sistemas e Informática
--------------------------------------------
Universidad Continental · Junín, Perú · 2026
```