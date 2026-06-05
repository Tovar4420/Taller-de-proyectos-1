"""
infrastructure/adapters/output/ml/
Adaptador de salida ML — implementa PrediccionRepositoryPort
usando Random Forest Regressor (scikit-learn).

Si en el futuro se cambia a XGBoost, red neuronal, o una API
externa de ML, solo se modifica este archivo.

NO accede a Firestore directamente: recibe los datos ya
preparados desde el use case a través del VisitaRepositoryPort.
"""

import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.preprocessing import LabelEncoder

from domain.ports.output import PrediccionRepositoryPort


# ── Feriados nacionales del Perú (mes, día) ───────────────────────
_FERIADOS = {
    (1, 1), (4, 1), (5, 1), (6, 29), (7, 28), (7, 29),
    (8, 30), (10, 8), (11, 1), (12, 8), (12, 25)
}


def _es_feriado(mes: int, dia: int) -> bool:
    return (mes, dia) in _FERIADOS


def _generar_datos_sinteticos(n: int = 900) -> tuple:
    """
    Genera n registros sintéticos calibrados con patrones reales
    de turismo en Junín (MINCETUR, estudios CCT 2021).
    Usados como base cuando los datos reales son insuficientes.
    """
    import random
    random.seed(42)
    np.random.seed(42)

    destinos_config = [
        ('Natural',   483,  'Gruta de Huagapo'),
        ('Natural',   300,  'Nevado Huaytapallana'),
        ('Natural',   500,  'Laguna de Paca'),
        ('Cultural',  1000, 'Valle del Perene'),
        ('Historico', 200,  'Convento de Ocopa'),
        ('Natural',   400,  'Reserva de Junin'),
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

        factor_feriado = 1.20 if _es_feriado(mes, dia + 1) else 1.0
        factor_cap     = 1.22 if capacidad <= 300 else (1.0 if capacidad <= 500 else 0.82)
        ruido          = random.uniform(-8, 8)

        ocupacion = min(100, max(0,
            base * factor_mes * factor_dia * factor_feriado * factor_cap + ruido
        ))

        X.append([dia, mes, categoria, capacidad])
        y.append(round(ocupacion, 1))

    return X, y


class RandomForestPrediccionAdapter(PrediccionRepositoryPort):
    """
    Implementacion del predictor de afluencia usando Random Forest.
    Intercambiable por cualquier otro algoritmo sin tocar el dominio.
    """

    DIAS  = ['Lunes', 'Martes', 'Miercoles', 'Jueves', 'Viernes', 'Sabado', 'Domingo']
    MESES = ['', 'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
             'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']

    def __init__(self):
        self._modelo   = None
        self._encoder  = None
        self._metricas = {}

    def modelo_listo(self) -> bool:
        return self._modelo is not None

    def obtener_metricas(self) -> dict:
        return self._metricas

    def entrenar(self, datos_reales: list) -> dict:
        n_reales       = len(datos_reales)
        X_sint, y_sint = _generar_datos_sinteticos(n=900)
        X_raw, y_raw   = [], []

        if datos_reales:
            factor_peso = max(1, 900 // max(n_reales, 1) // 3)
            for reg in datos_reales:
                for _ in range(factor_peso):
                    X_raw.append([reg[0], reg[1], reg[2], reg[3]])
                    y_raw.append(reg[4])
            print(f"Datos reales: {n_reales} registros (x{factor_peso} -> {len(X_raw)} filas)")

        X_raw.extend(X_sint)
        y_raw.extend(y_sint)

        self._encoder = LabelEncoder()
        todas_cats    = [r[2] for r in X_raw] + ['Natural', 'Cultural', 'Historico']
        self._encoder.fit(todas_cats)

        X = np.array([
            [r[0], r[1], self._encoder.transform([r[2]])[0], r[3]]
            for r in X_raw
        ])
        y = np.array(y_raw)

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        self._modelo = RandomForestRegressor(
            n_estimators=150, max_depth=10, random_state=42, n_jobs=-1
        )
        self._modelo.fit(X_train, y_train)

        y_pred = self._modelo.predict(X_test)
        mae    = mean_absolute_error(y_test, y_pred)
        r2     = r2_score(y_test, y_pred)

        self._metricas = {
            'algoritmo':              'Random Forest Regressor',
            'n_estimadores':          150,
            'exactitud_r2':           round(r2 * 100, 1),
            'error_mae':              round(mae, 2),
            'precision':              round((1 - mae / 100) * 100, 1),
            'datos_reales_firestore': n_reales,
            'datos_sinteticos':       len(X_sint),
            'datos_entrenamiento':    len(X_train),
            'datos_prueba':           len(X_test),
            'fuente_datos':           'Firestore + sinteticos' if n_reales > 0 else 'Solo sinteticos',
            'variables':              ['dia_semana', 'mes', 'categoria', 'capacidad_max'],
        }

        print(f"ML entrenado - R2: {self._metricas['exactitud_r2']}% | MAE: {mae:.2f}%")
        return self._metricas

    def predecir(self, dia_semana: int, mes: int, categoria: str, capacidad_max: int) -> dict:
        if not self.modelo_listo():
            raise RuntimeError('El modelo no ha sido entrenado todavia.')

        try:
            cat_encoded = self._encoder.transform([categoria])[0]
        except ValueError:
            cat_encoded = self._encoder.transform(['Natural'])[0]

        X          = np.array([[dia_semana, mes, cat_encoded, capacidad_max]])
        prediccion = float(self._modelo.predict(X)[0])
        prediccion = round(min(100, max(0, prediccion)), 1)

        if prediccion >= 90:
            estado, recomendacion, color = 'critico', 'No recomendado visitar en esta fecha', '#c0392b'
        elif prediccion >= 70:
            estado, recomendacion, color = 'alto', 'Visitar en la manana temprano para evitar aglomeraciones', '#e07b39'
        elif prediccion >= 40:
            estado, recomendacion, color = 'moderado', 'Buena opcion, afluencia dentro de lo normal', '#d4a017'
        else:
            estado, recomendacion, color = 'bajo', 'Excelente momento para visitar, poca afluencia', '#2d6a4f'

        return {
            'porcentaje_predicho': prediccion,
            'estado_predicho':     estado,
            'color_estado':        color,
            'recomendacion':       recomendacion,
            'para_dia':            self.DIAS[dia_semana],
            'para_mes':            self.MESES[mes],
            'metricas_modelo':     self._metricas,
        }
