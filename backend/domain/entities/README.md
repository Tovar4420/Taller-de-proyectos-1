# Entidades del Dominio

Esta carpeta representa las **entidades del núcleo** de la arquitectura hexagonal.
Las entidades encapsulan las reglas de negocio más puras del sistema.

## Entidades del sistema

### Destino
Representa un lugar turístico de la región Junín.
- Atributos: id, nombre, ubicacion, descripcion, categoria, capacidad_max, visitantes_actuales, latitud, longitud
- Reglas de negocio: cálculo de porcentaje de ocupación y estado (bajo/moderado/alto/crítico)
- Implementación actual: lógica en `backend/routes/destinos.py` → funciones `_porcentaje()` y `_estado()`

### Perfil
Representa a un usuario del sistema (turista o administrador).
- Atributos: id, nombre, nombre_perfil, tipo, fecha_creacion
- Implementación actual: `backend/routes/perfiles.py`

### Alerta
Representa una notificación de sobrecapacidad en un destino.
- Atributos: id, destino_id, destino, tipo (critica/advertencia), mensaje, activa, fecha
- Regla de negocio: no se duplican alertas activas del mismo tipo para el mismo destino
- Implementación actual: `backend/routes/destinos.py` → función `_generar_alerta_si_necesario()`

### Visita
Representa el registro de ingreso de visitantes a un destino.
- Atributos: destino_id, perfil_id, cantidad, fecha
- Implementación actual: colección `visitas` en Firestore, registrada desde `registrar_visita()`
