# Puertos de Salida (Output Ports)

Los **puertos de salida** definen lo que el dominio necesita del exterior para funcionar.
El dominio no sabe *cómo* se implementan, solo conoce el contrato.

## Puertos de salida definidos

### Puerto: Repositorio de Datos (IDestinoRepository)
El dominio necesita poder:
- Leer, crear y actualizar destinos turísticos
- Leer y crear registros de visitas
- Leer, crear y actualizar alertas
- Leer, crear y eliminar perfiles

### Puerto: Servicio de IA (IAsistenteIA)
El dominio necesita poder:
- Enviar un contexto de destinos y un historial de conversación
- Recibir una respuesta en lenguaje natural del modelo de IA

## Implementaciones (Adaptadores de Salida)

| Puerto                  | Adaptador implementado              | Tecnología        |
|-------------------------|-------------------------------------|-------------------|
| IDestinoRepository      | `config/firebase_init.py`           | Firebase Firestore|
| Carga inicial de datos  | `config/seed_data.py`               | Firebase Firestore|
| IAsistenteIA            | `frontend/scripts/asistente.js`     | Groq API / Llama 3.3 70B |
