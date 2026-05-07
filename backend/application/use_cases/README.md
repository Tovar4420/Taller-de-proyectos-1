# Casos de Uso (Application Layer)

La **capa de aplicación** orquesta el flujo entre los puertos de entrada y el dominio.
No contiene lógica de negocio pura, sino la coordinación de las operaciones.

## Casos de uso implementados

### CU-01: Registrar Visita
- **Actor:** Turista o administrador
- **Flujo:** Recibe destino_id y cantidad → valida capacidad disponible → actualiza contador → registra visita en BD → evalúa si debe generar alerta → retorna estado actualizado del destino
- **Implementación:** `routes/destinos.py` → `registrar_visita()`

### CU-02: Monitorear Afluencia
- **Actor:** Cualquier usuario
- **Flujo:** Solicita lista de destinos → consulta BD → calcula porcentaje y estado de cada uno → retorna lista ordenada
- **Implementación:** `routes/destinos.py` → `listar_destinos()`

### CU-03: Generar Alerta Automática
- **Actor:** Sistema (disparado por CU-01)
- **Flujo:** Evalúa porcentaje de ocupación → si ≥70% y no existe alerta activa del mismo tipo → crea alerta en BD
- **Implementación:** `routes/destinos.py` → `_generar_alerta_si_necesario()`

### CU-04: Consultar Asistente IA (Wayra)
- **Actor:** Turista
- **Flujo:** Recibe pregunta del usuario → construye contexto con datos en tiempo real de destinos → envía a Groq API → parsea respuesta y sugerencias → muestra al usuario
- **Implementación:** `frontend/scripts/asistente.js`

### CU-05: Gestionar Perfil de Turista
- **Actor:** Turista / Administrador
- **Flujo:** Crear, consultar o eliminar perfiles con validación de unicidad de nombre
- **Implementación:** `routes/perfiles.py`

### CU-06: Gestionar Alertas
- **Actor:** Administrador
- **Flujo:** Listar alertas activas / desactivar una alerta resuelta
- **Implementación:** `routes/alertas.py`
