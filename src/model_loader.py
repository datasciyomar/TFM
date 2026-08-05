"""
model_loader.py
───────────────
Carga y cacheo de modelos y pipeline.
Usa st.cache_resource para cargar modelos UNA sola vez y mantenerlos en memoria.
st.cache_resource es el mecanismo correcto para objetos pesados compartidos entre
sesiones (no st.cache_data, que serializa/deserializa en cada llamada).
"""

import os
import pickle
import logging
import numpy as np
import pandas as pd
import streamlit as st
import xgboost as xgb
import shap

logger = logging.getLogger(__name__)

# ─── RUTAS ───────────────────────────────────────────────────────────────────
# Ajustar si la estructura de carpetas difiere.
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(BASE_DIR, "models")
PROC_DIR = os.path.join(BASE_DIR, "data", "processed")


# ─── CARGA DE MODELOS ─────────────────────────────────────────────────────────


@st.cache_resource(show_spinner="Cargando modelos (solo la primera vez)…")
def load_xgb_model():
    """
    Carga el modelo XGBoost-AFT desde disco.
    xgb.Booster.load_model() es más rápido y seguro que pickle para XGBoost.
    """
    path = os.path.join(MODELS_DIR, "xgb_aft_model.ubj")
    if not os.path.exists(path):
        return None  # modo demo sin modelo real
    model = xgb.Booster()
    model.load_model(path)
    return model


@st.cache_resource(show_spinner="Cargando RSF…")
def load_rsf_model():
    """
    Carga el Random Survival Forest desde disco.
    """
    path = os.path.join(MODELS_DIR, "rsf_model.pkl")
    if not os.path.exists(path):
        return None
    with open(path, "rb") as f:
        return pickle.load(f)


@st.cache_resource(show_spinner="Cargando pipeline…")
def load_pipeline():
    """
    Carga los objetos del pipeline de preprocesado:
    encoders, imputation params, scaler, feature names.
    """
    path = os.path.join(PROC_DIR, "pipeline_objects.pkl")
    if not os.path.exists(path):
        return None
    with open(path, "rb") as f:
        return pickle.load(f)


@st.cache_resource(show_spinner="Inicializando SHAP explainer…")
def load_shap_explainer():
    """
    Construye el TreeExplainer de SHAP para el modelo XGBoost-AFT.
    """
    model = load_xgb_model()
    if model is None:
        return None

    pipeline = load_pipeline()
    feature_names = pipeline["feature_cols"] if pipeline else None

    # --- PARCHE DEFINITIVO PARA SHAP + XGBOOST AFT ---
    # Inyectamos el atributo 'base_score' directamente en la clase interna
    # de SHAP antes de que intente leer el modelo.
    try:
        from shap.explainers._tree import XGBTreeModelLoader

        # Le damos un valor por defecto de 0.5 a la clase
        if not hasattr(XGBTreeModelLoader, "base_score"):
            XGBTreeModelLoader.base_score = 0.5
    except Exception as e:
        logger.warning(f"Aviso: No se pudo aplicar el parche de SHAP ({e})")
    # -------------------------------------------------

    # Ahora TreeExplainer podrá instanciarse sin lanzar AttributeError
    try:
        return shap.TreeExplainer(model, feature_names=feature_names)
    except Exception as e:
        logger.warning(f"No se pudo instanciar TreeExplainer de SHAP: {e}")
        return None



# ─── CARGA DE DATOS DE VALIDACIÓN (para página de equidad) ───────────────────


@st.cache_data(show_spinner="Cargando datos de validación…")
def load_validation_data():
    """
    Carga el conjunto de validación preprocesado y las predicciones de riesgo.
    Devuelve un diccionario con todos los arrays necesarios para análisis de equidad.
    """
    result = {}

    # 1. Cargar DataFrames (Parquet) desde data/processed/
    for fname, key in [
        ("X_val.parquet", "X_val"),
        ("race_val.parquet", "race_val_df"),
    ]:
        path = os.path.join(PROC_DIR, fname)
        if os.path.exists(path):
            result[key] = pd.read_parquet(path)

    # 2. Cargar variables objetivo (Numpy) desde data/processed/
    for fname, key in [
        ("y_time_val.npy", "y_time"),
        ("y_event_val.npy", "y_event"),
    ]:
        path = os.path.join(PROC_DIR, fname)
        if os.path.exists(path):
            result[key] = np.load(path)
            if key == "y_event":
                result[key] = result[key].astype(bool)

    # 3. Cargar predicciones de los modelos (Numpy) desde models/
    for fname, key in [
        ("xgb_risk_val.npy", "xgb_risk"),
        ("rsf_risk_val.npy", "rsf_risk"),
    ]:
        path = os.path.join(MODELS_DIR, fname)
        if os.path.exists(path):
            result[key] = np.load(path)

    # Extraer el array de la columna race_group
    if "race_val_df" in result:
        result["race_val"] = result["race_val_df"]["race_group"].values

    return result


# ─── MODO DEMO ────────────────────────────────────────────────────────────────


def is_demo_mode():
    """
    Retorna True si los modelos no están disponibles en disco.
    En modo demo, la app muestra resultados simulados con disclaimer.
    """
    xgb_path = os.path.join(MODELS_DIR, "xgb_aft_model.ubj")
    return not os.path.exists(xgb_path)


def demo_prediction(risk_percentile: float = 0.65) -> dict:
    """
    Genera una predicción simulada para modo demo.
    risk_percentile: entre 0 y 1, controla el nivel de riesgo simulado.
    """
    np.random.seed(42)
    # Simular distribución de riesgo AFT (log-normal)
    log_t_pred = np.random.normal(loc=2.5 - risk_percentile * 2, scale=0.8)
    risk_score = -log_t_pred
    return {
        "risk_score": float(risk_score),
        "risk_percentile": risk_percentile,
        "risk_label": "Alto"
        if risk_percentile > 0.7
        else "Moderado"
        if risk_percentile > 0.4
        else "Bajo",
        "is_demo": True,
    }
