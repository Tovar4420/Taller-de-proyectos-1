# Adaptador de Salida — Firebase Firestore

Este es el **adaptador de salida de base de datos** del sistema.
Implementa el puerto de repositorio de datos usando Firebase Firestore como tecnología de persistencia.

## Archivos que implementan este adaptador

| Archivo                          | Responsabilidad                                      |
|----------------------------------|------------------------------------------------------|
| `backend/config/firebase_init.py` | Inicializa la conexión con Firebase usando credenciales y expone `get_db()` |
| `backend/config/seed_data.py`     | Carga los 6 destinos turísticos iniciales de Junín en Firestore (solo si no existen) |

## Colecciones en Firestore

| Colección   | Descripción                                          |
|-------------|------------------------------------------------------|
| `destinos`  | Documentos de cada destino turístico con su afluencia en tiempo real |
| `visitas`   | Registro histórico de cada visita registrada          |
| `perfiles`  | Usuarios del sistema (turistas / administradores)    |
| `alertas`   | Alertas de sobrecapacidad generadas automáticamente  |

## Destinos iniciales cargados (seed_data.py)

1. Reserva Paisajística Nor Yauyos-Cochas
2. Lago Junín (Chinchaycocha)
3. Centro Histórico de Huancayo
4. Santuario Histórico de Chupaca
5. Bosque de Piedras de Huayllay
6. Nevado Huaytapallana

## Tecnología
- **SDK:** firebase-admin 6.5.0
- **Base de datos:** Cloud Firestore (NoSQL - documentos)
- **Autenticación:** Service Account (firebase_credentials.json)
