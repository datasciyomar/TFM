"""
preprocessing.py
────────────────
Pipeline de preprocesado para inferencia sobre un paciente individual.

PRINCIPIO CRÍTICO: Este módulo usa los parámetros aprendidos en el entrenamiento
(medianas, modas, encoders) cargados desde pipeline_objects.pkl.
NUNCA recalcula estadísticas a partir de los datos del paciente actual.
Esto garantiza que la predicción es consistente con el modelo entrenado.
"""

import numpy as np
import pandas as pd
from typing import Optional


# ─── CONSTANTES ───────────────────────────────────────────────────────────────

# Variables con patrón MNAR estructural → NA codificado como categoría
MNAR_VARS = [
    "tce_match",
    "tce_div_match",
    "tce_imm_match",
    "mrd_hct",
    "cyto_score",
    "cyto_score_detail",
]

# Comorbilidades: NA → "No_evaluado"
CAT_NA_AS_CATEGORY = [
    "diabetes",
    "obesity",
    "cardiac",
    "arrhythmia",
    "renal_issue",
    "pulm_severe",
    "pulm_moderate",
    "hepatic_severe",
    "hepatic_mild",
    "peptic_ulcer",
    "rheum_issue",
    "psych_disturb",
    "prior_tumor",
    "vent_hist",
    "conditioning_intensity",
    "melphalan_dose",
]

# Variables HLA con indicador de missing
HLA_NUM_VARS = [
    "hla_match_c_high",
    "hla_high_res_8",
    "hla_low_res_6",
    "hla_high_res_6",
    "hla_high_res_10",
    "hla_match_dqb1_high",
    "hla_nmdp_6",
    "hla_match_c_low",
    "hla_match_drb1_low",
    "hla_match_dqb1_low",
    "hla_match_a_high",
    "hla_match_b_low",
    "hla_match_a_low",
    "hla_match_b_high",
    "hla_low_res_8",
    "hla_match_drb1_high",
    "hla_low_res_10",
]


# ─── FUNCIONES DE FEATURE ENGINEERING ────────────────────────────────────────


def create_clinical_features(X: pd.DataFrame) -> pd.DataFrame:
    """
    Crea variables derivadas clínicamente relevantes sobre un DataFrame de pacientes.
    Idéntico al aplicado durante el entrenamiento (NB02).
    """
    X = X.copy()

    # Grupo de edad
    X["age_group"] = pd.cut(
        X["age_at_hct"],
        bins=[-np.inf, 2, 17, 39, 59, np.inf],
        labels=[
            "Neonato/Infante",
            "Pediátrico",
            "Adulto joven",
            "Adulto medio",
            "Adulto mayor",
        ],
    ).astype(str)

    # Diferencia edad donante-receptor
    X["donor_recip_age_diff"] = X["donor_age"] - X["age_at_hct"]

    # Indicador donante mayor que receptor en >10 años
    X["donor_older_than_recip"] = (X["donor_age"] > X["age_at_hct"] + 10).astype(int)

    # Índice Sorror categorizado
    X["sorror_cat"] = pd.cut(
        X["comorbidity_score"], bins=[-np.inf, 0, 2, np.inf], labels=["0", "1-2", ">=3"]
    ).astype(str)

    # KPS bajo
    X["kps_low"] = (X["karnofsky_score"] < 70).astype(int)

    # HLA 10/10 completo
    X["hla10_full_match"] = (X["hla_high_res_10"] >= 10.0).astype(int)

    # Donante no emparentado
    X["unrelated_donor"] = (X["donor_related"].astype(str) == "Unrelated").astype(int)

    # TBI utilizada
    X["tbi_used"] = (X["tbi_status"].astype(str) != "No TBI").astype(int)

    # Años desde era TCE
    X["years_since_tce_era"] = np.maximum(0, X["year_hct"] - 2015)

    # Período del HCT
    X["hct_era"] = pd.cut(
        X["year_hct"],
        bins=[-np.inf, 2012, 2016, np.inf],
        labels=["Early (2008-2012)", "Mid (2013-2016)", "Modern (2017+)"],
    ).astype(str)

    return X


def preprocess_patient(
    patient_dict: dict, pipeline_objects: dict, feature_cols: Optional[list] = None
) -> pd.DataFrame:
    """
    Preprocesa un único paciente para inferencia.

    Parameters
    ----------
    patient_dict : dict
        Diccionario con los valores clínicos del paciente.
    pipeline_objects : dict
        Objetos del pipeline cargados desde pipeline_objects.pkl.
    feature_cols : list, optional
        Lista de columnas esperadas por el modelo.

    Returns
    -------
    pd.DataFrame
        DataFrame de una fila con todas las variables preprocesadas y codificadas.
    """
    df = pd.DataFrame([patient_dict])

    # 1. Imputación MNAR → categoría informativa
    for v in MNAR_VARS:
        if v in df.columns:
            df[v] = df[v].fillna("No_disponible").astype(str)

    for v in CAT_NA_AS_CATEGORY:
        if v in df.columns:
            df[v] = df[v].fillna("No_evaluado").astype(str)

    # 2. Indicadores de missing HLA (antes de imputar)
    hla_indicators = {}
    for v in HLA_NUM_VARS:
        if v in df.columns:
            hla_indicators[v + "_missing"] = int(df[v].isnull().values[0])

    # 3. Imputación por mediana/moda de TRAIN
    imputation_params = pipeline_objects.get("imputation_params", {})

    for v, med in imputation_params.get("medians_num", {}).items():
        if v in df.columns:
            df[v] = df[v].fillna(med)

    for v, mode_val in imputation_params.get("modes_cat", {}).items():
        if v in df.columns:
            df[v] = df[v].fillna(mode_val).astype(str)

    # 4. Añadir indicadores de missing HLA
    for k, val in hla_indicators.items():
        df[k] = val

    # 5. Feature engineering clínico
    df = create_clinical_features(df)

    # 6. Encoding con los encoders de TRAIN
    label_encoders = pipeline_objects.get("label_encoders", {})
    cat_cols = df.select_dtypes(include=["object"]).columns.tolist()

    for col in cat_cols:
        if col in label_encoders:
            le = label_encoders[col]
            known = set(le.classes_)
            val = str(df[col].values[0])
            df[col] = le.transform([val if val in known else le.classes_[0]])[0]
        else:
            # Variable nueva no vista en entrenamiento: codificar como 0
            df[col] = 0

    # 7. Asegurar las columnas esperadas por el modelo
    if feature_cols:
        for col in feature_cols:
            if col not in df.columns:
                df[col] = 0  # valor por defecto para columnas faltantes
        df = df[feature_cols]

    return df


def risk_to_label(
    risk_score: float, low_thresh: float = -0.5, high_thresh: float = 0.5
) -> str:
    """
    Convierte un risk score continuo del modelo AFT en una etiqueta clínica.

    El modelo XGBoost-AFT predice log(tiempo de supervivencia).
    Se invierte el signo: risk_score = -log_t_pred.
    Valores altos = mayor riesgo (menor tiempo esperado hasta evento).

    Los umbrales se calibran sobre los percentiles del conjunto de validación.
    """
    if risk_score > high_thresh:
        return "Alto"
    elif risk_score > low_thresh:
        return "Moderado"
    else:
        return "Bajo"


def risk_to_color(label: str) -> str:
    """Devuelve el color CSS correspondiente al nivel de riesgo."""
    return {
        "Alto": "#C00000",
        "Moderado": "#D48806",
        "Bajo": "#3B6D11",
    }.get(label, "#595959")
