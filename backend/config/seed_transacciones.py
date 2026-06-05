"""
config/seed_transacciones.py
════════════════════════════════════════════════════════════════════
Script de generación de datos masivos para TurismoJunín
MODIFICACIÓN: Protege destinos llenos y rellena el resto entre 20% y 43%.
════════════════════════════════════════════════════════════════════
"""

import random
import sys
import os
from datetime import datetime, timedelta, timezone
from collections import defaultdict

# ── Asegurar que el backend esté en el path ───────────────────────
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.firebase_init import init_firebase, get_db

# ══════════════════════════════════════════════════════════════════
# CONFIGURACIÓN
# ══════════════════════════════════════════════════════════════════
TOTAL_TRANSACCIONES_OBJETIVO = 750   # Exigencia de la rúbrica
FECHA_INICIO  = datetime(2025, 12, 1,  tzinfo=timezone.utc)
FECHA_FIN     = datetime(2026, 5, 27,  tzinfo=timezone.utc)
RANDOM_SEED   = 42

FERIADOS = {
    (12, 25), (12, 31), (1, 1),   # Navidad, Fin de Año, Año Nuevo
    (4, 17),  (4, 18),  (4, 20),  # Semana Santa 2026
    (5, 1),                        # Día del Trabajo
}

PERFILES_PRUEBA = [
    ("Ana García",       "ana_garcia",       "turista"),
    ("Luis Quispe",      "luis_quispe",      "turista"),
    ("María Torres",     "maria_torres",     "turista"),
    ("Carlos Huamán",    "carlos_huaman",    "turista"),
    ("Rosa Mendoza",     "rosa_mendoza",     "turista"),
    ("Jorge Flores",     "jorge_flores",     "turista"),
    ("Patricia Rojas",   "patricia_rojas",   "turista"),
    ("Miguel Castillo",  "miguel_castillo",  "turista"),
    ("Lucía Vargas",     "lucia_vargas",     "turista"),
    ("Roberto Chávez",   "roberto_chavez",   "turista"),
    ("Elena Mamani",     "elena_mamani",     "turista"),
    ("Diego Salazar",    "diego_salazar",    "turista"),
    ("Carmen Ccopa",     "carmen_ccopa",     "turista"),
    ("Andrés Pariona",   "andres_pariona",   "turista"),
    ("Sofía Condori",    "sofia_condori",    "turista"),
]

# ══════════════════════════════════════════════════════════════════
# FUNCIONES AUXILIARES DE FLUJO
# ══════════════════════════════════════════════════════════════════

def _es_feriado(fecha: datetime) -> bool:
    return (fecha.month, fecha.day) in FERIADOS

def _factor_dia(dia_semana: int) -> float:
    factores = {0: 0.55, 1: 0.60, 2: 0.65, 3: 0.70, 4: 0.90, 5: 1.30, 6: 1.20}
    return factores[dia_semana]

def _factor_mes(mes: int) -> float:
    factores = {1: 1.15, 2: 0.85, 3: 0.90, 4: 1.20, 5: 1.25, 6: 1.10, 7: 1.30, 8: 1.20, 9: 1.05, 10: 0.80, 11: 0.75, 12: 1.10}
    return factores.get(mes, 1.0)

def _factor_categoria(categoria: str) -> float:
    return {'Natural': 1.15, 'Cultural': 0.90, 'Histórico': 0.80}.get(categoria, 1.0)

def _cantidad_visita(destino_info: dict, fecha: datetime) -> int:
    r = random.random()
    if r < 0.30: return 1
    elif r < 0.55: return random.randint(2, 3)
    elif r < 0.80: return random.randint(4, 7)
    elif r < 0.95: return random.randint(8, 15)
    else: return random.randint(16, 30)

def _fecha_aleatoria_en_rango(inicio: datetime, fin: datetime) -> datetime:
    delta = fin - inicio
    segundos = int(delta.total_seconds())
    offset = random.randint(0, segundos)
    fecha = inicio + timedelta(seconds=offset)
    return fecha.replace(hour=random.randint(7, 17), minute=random.randint(0, 59), second=0, microsecond=0)

# ══════════════════════════════════════════════════════════════════
# PASOS MODIFICADOS
# ══════════════════════════════════════════════════════════════════

def obtener_destinos(db) -> list[dict]:
    docs = list(db.collection('destinos').stream())
    if not docs:
        print("❌ No se encontraron destinos en Firestore.")
        sys.exit(1)

    destinos = []
    for doc in docs:
        d = doc.to_dict()
        destinos.append({
            'id':                  doc.id,
            'nombre':              d.get('nombre', ''),
            'categoria':           d.get('categoria', 'Natural'),
            'capacidad':           d.get('capacidad_max', 300),
            'visitantes_actuales': d.get('visitantes_actuales', 0)  # <-- Mapeamos el estado actual
        })
    return destinos


def asegurar_perfiles(db) -> list[str]:
    existentes = list(db.collection('perfiles').stream())
    if len(existentes) >= 15:
        return [d.id for d in existentes]

    perfiles_ref = db.collection('perfiles')
    ids_creados  = [d.id for d in existentes]
    nombres_existentes = {d.to_dict().get('nombre_perfil') for d in existentes}

    for nombre, nombre_perfil, tipo in PERFILES_PRUEBA:
        if nombre_perfil in nombres_existentes: continue
        doc_ref = perfiles_ref.add({
            'nombre': nombre, 'nombre_perfil': nombre_perfil, 'tipo': tipo,
            'fecha_creacion': datetime.now(timezone.utc).isoformat()
        })
        ids_creados.append(doc_ref[1].id)
    return ids_creados


def generar_transacciones(destinos: list, perfil_ids: list, total: int) -> list[dict]:
    random.seed(RANDOM_SEED)
    pesos = []
    for d in destinos:
        w = _factor_categoria(d['categoria']) * (1 + d['capacidad'] / 2000)
        pesos.append(w)

    transacciones = []
    intentos = 0
    while len(transacciones) < total and intentos < total * 10:
        intentos += 1
        fecha = _fecha_aleatoria_en_rango(FECHA_INICIO, FECHA_FIN)
        destino = random.choices(destinos, weights=pesos, k=1)[0]

        prob = _factor_dia(fecha.weekday()) * _factor_mes(fecha.month) * _factor_categoria(destino['categoria'])
        if _es_feriado(fecha): prob *= 1.35

        if random.random() > (prob / 2.5) + 0.60 - 0.60: continue

        transacciones.append({
            'destino_id':      destino['id'],
            'perfil_id':       random.choice(perfil_ids),
            'cantidad':        _cantidad_visita(destino, fecha),
            'fecha':           fecha.isoformat(),
            '_destino_nombre': destino['nombre']
        })

    transacciones.sort(key=lambda x: x['fecha'])
    return transacciones


def escribir_en_firestore(db, transacciones: list[dict]) -> int:
    col = db.collection('visitas')
    BATCH_SIZE = 400
    escritos = 0

    for i in range(0, len(transacciones), BATCH_SIZE):
        lote = transacciones[i : i + BATCH_SIZE]
        batch = db.batch()
        for tx in lote:
            batch.set(col.document(), tx)
        batch.commit()
        escritos += len(lote)
    return escritos


def actualizar_visitantes_actuales(db, destinos_a_actualizar: list):
    """
    Asigna un volumen de visitas controlado (entre 20% y 43%)
    ÚNICAMENTE a los destinos que necesitan relleno.
    """
    col = db.collection('destinos')
    print(f"\n📊 Rellenando afluencia en tiempo real para destinos secundarios...")
    
    for destino in destinos_a_actualizar:
        # Generamos un porcentaje aleatorio entre el 20% y el 43%
        porcentaje_simulado = random.randint(20, 43) / 100.0
        actuales = int(destino['capacidad'] * porcentaje_simulado)
        
        # Guardar en Firestore
        col.document(destino['id']).update({'visitantes_actuales': actuales})
        print(f"   ✔ {destino['nombre']}: Fijado en {actuales} visitantes ({int(porcentaje_simulado*100)}% de cap.)")


# ══════════════════════════════════════════════════════════════════
# CONTROLADOR PRINCIPAL (MAIN)
# ══════════════════════════════════════════════════════════════════

def main():
    print("\n" + "═"*68)
    print("🌿 SEEDER OPTIMIZADO — CONTROL DE CAPACIDADES JUNÍN")
    print("═"*68)

    init_firebase()
    db = get_db()

    # 1. Obtener todos los destinos desde la BD
    todos_los_destinos = obtener_destinos(db)
    
    destinos_para_historial = []
    destinos_para_relleno = []

    print("\n🛡️ Analizando estado actual de los destinos en la interfaz:")
    for d in todos_los_destinos:
        porcentaje_ui = (d['visitantes_actuales'] / d['capacidad']) if d['capacidad'] > 0 else 0
        
        # Regla de oro: Si está al 80% o más, o es uno de tus dos destinos bandera, NO SE TOCA.
        if porcentaje_ui >= 0.80 or d['nombre'] in ["Convento de Ocopa", "Nevado Huaytapallana"]:
            print(f"   ⚠️ [IGNORADO/PROTEGIDO] {d['nombre']} se queda intacto al {int(porcentaje_ui*100)}% ({d['visitantes_actuales']} visitantes).")
        else:
            print(f"   🟢 [APTO PARA RELLENO] {d['nombre']} pasará a simulación.")
            destinos_para_historial.append(d)
            destinos_para_relleno.append(d)

    if not destinos_para_relleno:
        print("\n❌ Todos los destinos ya están llenos o protegidos. Nada que hacer.")
        return

    perfil_ids = asegurar_perfiles(db)

    # 2. Generar el historial masivo solo para los destinos permitidos (Exigencia rúbrica)
    print(f"\n🎲 Generando {TOTAL_TRANSACCIONES_OBJETIVO} visitas históricas de respaldo...")
    txs = generar_transacciones(destinos_para_historial, perfil_ids, TOTAL_TRANSACCIONES_OBJETIVO)

    # 3. Guardar el historial en la colección 'visitas'
    print(f"🔥 Subiendo transacciones a Firestore...")
    total_escritos = escribir_en_firestore(db, txs)
    print(f"   ✔ Se guardaron {total_escritos} documentos históricos con éxito.")

    # 4. Actualizar el estado en tiempo real con el rango 20% - 43%
    actualizar_visitantes_actuales(db, destinos_para_relleno)

    print("\n═" * 68)
    print("🎉 ¡PROCESO TERMINADO CON ÉXITO!")
    print("Los destinos críticos mantuvieron su valor y los demás se rellenaron idealmente.")
    print("═" * 68 + "\n")

if __name__ == '__main__':
    main()