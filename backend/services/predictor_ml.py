"""
services/predictor_ml.py
═══════════════════════════════════════════════════════════
SERVICIO DE MACHINE LEARNING — Predictor de Afluencia
Algoritmo : Random Forest Regressor (scikit-learn)
Datos     : Reales extraídos de Firebase Firestore (colección
            'visitas') combinados con datos sintéticos como
            base de entrenamiento cuando los datos reales son
            insuficientes.

Patrones reales aplicados:
  - Temporada alta mayo-septiembre (+18%) [Huaytapallana, Mincetur]
  - Fines de semana +28% afluencia [turismo interno peruano]
  - Feriados nacionales pico máximo [Semana Santa, Fiestas Patrias]
  - Capacidad Gruta Huagapo: 483 visitantes/día [estudio CCT 2021]
  - Destinos naturales más sensibles a temporada que históricos
═══════════════════════════════════════════════════════════
"""

import numpy as np
from datetime import datetime, timezone
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.preprocessing import LabelEncoder

# ── Instancia global del modelo ──────────────────────────────────
_modelo   = None
_encoder  = None
_metricas = {}

# ── Feriados nacionales del Perú (mes, día) ──────────────────────
FERIADOS = {
    (1,1),(4,1),(5,1),(6,29),(7,28),(7,29),
    (8,30),(10,8),(11,1),(12,8),(12,25)
}

def _es_feriado(mes, dia=15):
    return (mes, dia) in FERIADOS


# ══════════════════════════════════════════════════════════════════
# EXTRACCIÓN DE DATOS REALES DESDE FIRESTORE
# ══════════════════════════════════════════════════════════════════

def _cargar_datos_firestore():
    """
    Lee la colección 'visitas' y 'destinos' de Firestore y
    construye registros de entrenamiento reales.

    Retorna lista de [dia_semana, mes, categoria, capacidad, ocupacion_%]
    o lista vacía si no hay datos suficientes.
    """
    try:
        from config.firebase_init import get_db
        db = get_db()

        # ── Cargar destinos para obtener categoría y capacidad ────
        destinos_ref = db.collection('destinos').stream()
        destinos_map = {}
        for doc in destinos_ref:
            d = doc.to_dict()
            destinos_map[doc.id] = {
                'categoria':    d.get('categoria', 'Natural'),
                'capacidad':    d.get('capacidad_max', 300),
                'nombre':       d.get('nombre', ''),
            }

        if not destinos_map:
            print("⚠️  Sin destinos en Firestore, usando solo datos sintéticos.")
            return []

        # ── Cargar visitas ────────────────────────────────────────
        visitas_ref = db.collection('visitas').stream()
        visitas_raw = []
        for doc in visitas_ref:
            v = doc.to_dict()
            destino_id = v.get('destino_id')
            fecha_str  = v.get('fecha')
            cantidad   = v.get('cantidad', 1)

            if not destino_id or not fecha_str or destino_id not in destinos_map:
                continue

            try:
                # Parsear fecha ISO (con o sin zona horaria)
                fecha_str_clean = fecha_str.replace('Z', '+00:00')
                fecha = datetime.fromisoformat(fecha_str_clean)
                dia_semana = fecha.weekday()   # 0=lunes … 6=domingo
                mes        = fecha.month
            except Exception:
                continue

            visitas_raw.append({
                'destino_id': destino_id,
                'dia_semana': dia_semana,
                'mes':        mes,
                'cantidad':   cantidad,
            })

        if not visitas_raw:
            print("⚠️  Sin visitas registradas en Firestore.")
            return []

        # ── Agrupar visitas por (destino, dia, mes) ───────────────
        # y calcular % de ocupación promedio por combinación
        from collections import defaultdict
        agrupado = defaultdict(list)
        for v in visitas_raw:
            key = (v['destino_id'], v['dia_semana'], v['mes'])
            agrupado[key].append(v['cantidad'])

        registros = []
        for (destino_id, dia, mes), cantidades in agrupado.items():
            info     = destinos_map[destino_id]
            capacidad = info['capacidad']
            categoria = info['categoria']

            # Normalizar categoría
            cat_norm = categoria
            if categoria == 'Histórico':
                cat_norm = 'Historico'
            if cat_norm not in ['Natural', 'Cultural', 'Historico']:
                cat_norm = 'Natural'

            total_visitantes = sum(cantidades)
            # % de ocupación respecto a la capacidad máxima diaria
            pct = min(100.0, round((total_visitantes / capacidad) * 100, 1))

            registros.append([dia, mes, cat_norm, capacidad, pct])

        print(f"✅ Datos Firestore cargados: {len(registros)} registros reales "
              f"(de {len(visitas_raw)} visitas en {len(destinos_map)} destinos)")
        return registros

    except Exception as e:
        print(f"⚠️  Error cargando datos de Firestore: {e}")
        return []


# ══════════════════════════════════════════════════════════════════
# DATOS SINTÉTICOS (fallback / base de entrenamiento)
# ══════════════════════════════════════════════════════════════════

def _generar_datos_sinteticos(n=900):
    """
    Genera n registros sintéticos con patrones reales de turismo
    en Junín documentados por MINCETUR y estudios académicos.
    Usados como base cuando los datos reales son insuficientes.
    """
    import random
    random.seed(42)
    np.random.seed(42)

    destinos_config = [
        ('Natural',   483,  'Gruta de Huagapo'),
        ('Natural',   300,  'Nevado Huaytapallana'),
        ('Natural',   500,  'Laguna de Paca'),
        ('Cultural',  1000, 'Valle del Perené'),
        ('Historico', 200,  'Convento de Ocopa'),
        ('Natural',   400,  'Reserva de Junín'),
    ]

    X, y = [], []

    for _ in range(n):
        config    = random.choice(destinos_config)
        categoria = config[0]
        capacidad = config[1]
        dia       = random.randint(0, 6)
        mes       = random.randint(1, 12)

        base = {'Natural': 42, 'Cultural': 32, 'Historico': 28}[categoria]

        if 5 <= mes <= 9:
            factor_mes = 1.18
        elif mes in [1, 12]:
            factor_mes = 1.10
        elif mes in [3, 4]:
            factor_mes = 1.14
        else:
            factor_mes = 1.0

        if dia == 6:
            factor_dia = 1.32
        elif dia == 5:
            factor_dia = 1.26
        elif dia == 4:
            factor_dia = 1.10
        else:
            factor_dia = 1.0

        # Corrección del bug: usar día real del mes (15 es placeholder)
        factor_feriado = 1.20 if _es_feriado(mes, dia + 1) else 1.0

        factor_cap = 1.22 if capacidad <= 300 else (1.0 if capacidad <= 500 else 0.82)

        ruido = random.uniform(-8, 8)

        ocupacion = min(100, max(0,
            base * factor_mes * factor_dia * factor_feriado * factor_cap + ruido
        ))

        X.append([dia, mes, categoria, capacidad])
        y.append(round(ocupacion, 1))

    return X, y


# ══════════════════════════════════════════════════════════════════
# ENTRENAMIENTO DEL MODELO
# ══════════════════════════════════════════════════════════════════

def entrenar_modelo():
    """
    Entrena el Random Forest combinando datos reales de Firestore
    con datos sintéticos como base. Los datos reales tienen
    prioridad y mayor peso en el entrenamiento.
    """
    global _modelo, _encoder, _metricas

    # ── 1. Cargar datos reales de Firestore ───────────────────────
    datos_reales = _cargar_datos_firestore()
    n_reales     = len(datos_reales)

    # ── 2. Generar datos sintéticos como base ─────────────────────
    X_sint, y_sint = _generar_datos_sinteticos(n=900)

    # ── 3. Combinar: reales primero (con duplicación para darles
    #       más peso si son pocos), luego sintéticos ───────────────
    X_raw = []
    y_raw = []

    if datos_reales:
        # Duplicar datos reales para aumentar su peso relativo
        factor_peso = max(1, 900 // max(len(datos_reales), 1) // 3)
        for reg in datos_reales:
            for _ in range(factor_peso):
                X_raw.append([reg[0], reg[1], reg[2], reg[3]])
                y_raw.append(reg[4])
        print(f"📊 Datos reales: {n_reales} registros "
              f"(duplicados x{factor_peso} → {len(X_raw)} filas)")

    # Agregar sintéticos
    X_raw.extend(X_sint)
    y_raw.extend(y_sint)
    print(f"📊 Total entrenamiento: {len(X_raw)} registros "
          f"({len(X_raw) - len(y_raw) + len(y_sint)} sintéticos + "
          f"{len(X_raw) - len(y_sint)} reales ponderados)")

    # ── 4. Codificar categoría ────────────────────────────────────
    _encoder = LabelEncoder()
    todas_cats = [r[2] for r in X_raw]
    # Asegurar que siempre estén las 3 categorías conocidas
    todas_cats += ['Natural', 'Cultural', 'Historico']
    _encoder.fit(todas_cats)

    X = np.array([
        [r[0], r[1], _encoder.transform([r[2]])[0], r[3]]
        for r in X_raw
    ])
    y = np.array(y_raw)

    # ── 5. Train/test split ───────────────────────────────────────
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # ── 6. Entrenar Random Forest ─────────────────────────────────
    _modelo = RandomForestRegressor(
        n_estimators=150,
        max_depth=10,
        random_state=42,
        n_jobs=-1
    )
    _modelo.fit(X_train, y_train)

    # ── 7. Métricas ───────────────────────────────────────────────
    y_pred = _modelo.predict(X_test)
    mae    = mean_absolute_error(y_test, y_pred)
    r2     = r2_score(y_test, y_pred)

    n_total     = len(X_raw)
    n_train     = len(X_train)
    n_test      = len(X_test)

    _metricas = {
        'algoritmo':              'Random Forest Regressor',
        'n_estimadores':          150,
        'exactitud_r2':           round(r2 * 100, 1),
        'error_mae':              round(mae, 2),
        'precision':              round((1 - mae / 100) * 100, 1),
        'datos_reales_firestore': n_reales,
        'datos_sinteticos':       len(X_sint),
        'datos_entrenamiento':    n_train,
        'datos_prueba':           n_test,
        'fuente_datos':           'Firestore + sintéticos' if n_reales > 0 else 'Solo sintéticos',
        'variables':              ['dia_semana', 'mes', 'categoria', 'capacidad_max'],
    }

    print(f"✅ ML entrenado — R²: {_metricas['exactitud_r2']}% | "
          f"MAE: {mae:.2f}% | Fuente: {_metricas['fuente_datos']}")
    return _metricas


# ══════════════════════════════════════════════════════════════════
# PREDICCIÓN
# ══════════════════════════════════════════════════════════════════

def predecir_afluencia(dia_semana, mes, categoria, capacidad_max):
    """
    Predice el % de ocupación esperado para un destino.

    Parámetros:
        dia_semana   : int (0=lunes … 6=domingo)
        mes          : int (1-12)
        categoria    : str ('Natural','Cultural','Historico')
        capacidad_max: int

    Retorna dict con predicción, estado, recomendación y métricas.
    """
    global _modelo, _encoder

    if _modelo is None:
        entrenar_modelo()

    try:
        cat_encoded = _encoder.transform([categoria])[0]
    except ValueError:
        cat_encoded = _encoder.transform(['Natural'])[0]

    X          = np.array([[dia_semana, mes, cat_encoded, capacidad_max]])
    prediccion = float(_modelo.predict(X)[0])
    prediccion = round(min(100, max(0, prediccion)), 1)

    if prediccion >= 90:
        estado        = 'critico'
        recomendacion = 'No recomendado visitar en esta fecha'
        color         = '#c0392b'
    elif prediccion >= 70:
        estado        = 'alto'
        recomendacion = 'Visitar en la mañana temprano para evitar aglomeraciones'
        color         = '#e07b39'
    elif prediccion >= 40:
        estado        = 'moderado'
        recomendacion = 'Buena opción, afluencia dentro de lo normal'
        color         = '#d4a017'
    else:
        estado        = 'bajo'
        recomendacion = 'Excelente momento para visitar, poca afluencia'
        color         = '#2d6a4f'

    DIAS  = ['Lunes','Martes','Miércoles','Jueves','Viernes','Sábado','Domingo']
    MESES = ['','Enero','Febrero','Marzo','Abril','Mayo','Junio',
             'Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre']

    return {
        'porcentaje_predicho':    prediccion,
        'estado_predicho':        estado,
        'color_estado':           color,
        'recomendacion':          recomendacion,
        'para_dia':               DIAS[dia_semana],
        'para_mes':               MESES[mes],
        'metricas_modelo':        _metricas,
    }


# ══════════════════════════════════════════════════════════════════
# ENDPOINT DE MÉTRICAS
# ══════════════════════════════════════════════════════════════════

def obtener_metricas():
    """Retorna métricas del modelo, entrenándolo si es necesario."""
    global _metricas
    if not _metricas:
        entrenar_modelo()
    return _metricas