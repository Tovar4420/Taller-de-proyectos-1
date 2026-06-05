# Puertos de Entrada (Input Ports)

Los **puertos de entrada** definen los contratos que el exterior puede invocar sobre el dominio.
Son las operaciones que el sistema expone hacia el mundo exterior.

## Puertos definidos en este sistema

### Puerto: Gestión de Destinos
- `listar_destinos(categoria?)` → lista todos los destinos, con filtro opcional por categoría
- `obtener_destino(id)` → retorna un destino específico
- `registrar_visita(destino_id, cantidad, perfil_id?)` → incrementa visitantes y genera alerta si corresponde
- `registrar_salida(destino_id, cantidad)` → decrementa visitantes

### Puerto: Gestión de Perfiles
- `listar_perfiles()` → lista todos los perfiles con su conteo de visitas
- `crear_perfil(nombre, nombre_perfil, tipo)` → registra un nuevo usuario
- `obtener_perfil(id)` → retorna un perfil específico
- `eliminar_perfil(id)` → elimina un perfil del sistema

### Puerto: Gestión de Alertas
- `listar_alertas()` → retorna todas las alertas activas
- `desactivar_alerta(id)` → marca una alerta como resuelta

## Implementación (Adaptador de Entrada)
Estos puertos son implementados por los controladores REST en:
- `backend/routes/destinos.py`
- `backend/routes/perfiles.py`
- `backend/routes/alertas.py`
