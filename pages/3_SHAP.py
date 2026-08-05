"""
3_SHAP.py
─────────
Página de interpretabilidad global: bar plot, dependence plots
y heatmap de importancia SHAP por grupo racial.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import xgboost as xgb
import statsmodels.api as sm

from src.model_loader import (
    load_xgb_model,
    load_pipeline,
    load_shap_explainer,
    load_validation_data,
    is_demo_mode,
)
from src.config import LABEL_MAP, RACE_PALETTE, DOMAIN_COLORS

RACE_ORDER = list(RACE_PALETTE.keys())

st.set_page_config(page_title="SHAP HCT", page_icon="🔍", layout="wide")

from src.theme import apply_theme
apply_theme()

st.title("🔍 Interpretabilidad SHAP")
st.markdown("""
Análisis de los valores SHAP (SHapley Additive exPlanations) sobre el conjunto de validación.
Los valores SHAP cuantifican la contribución de cada variable a la predicción del modelo.
**SHAP > 0 → aumenta el riesgo predicho · SHAP < 0 → reduce el riesgo predicho.**
""")

DEMO = is_demo_mode()
pipeline = load_pipeline()
xgb_model = load_xgb_model()
explainer = load_shap_explainer()
val_data = load_validation_data()
DATA_OK = bool(val_data and "X_val" in val_data)

# Etiquetas dinámicas desde config.py
def get_label(col):
    return LABEL_MAP.get(col, col)

@st.cache_data(show_spinner="Calculando SHAP (puede tardar 1-2 minutos)…")
def compute_global_shap(_val_data, _pipeline, _explainer, _xgb_model):
    if not _val_data or "X_val" not in _val_data or _explainer is None:
        return None, None, None
    X_val = _val_data["X_val"]
    race_val = _val_data.get("race_val", np.array([]))
    
    # Muestra estratificada
    np.random.seed(42)
    sample_idx = []
    for race in RACE_ORDER:
        idx = np.where(race_val == race)[0]
        n = min(160, len(idx))
        if n > 0:
            sample_idx.extend(np.random.choice(idx, n, replace=False))
    
    X_sample = X_val.iloc[sample_idx]
    race_sample = race_val[sample_idx]
    dmat = xgb.DMatrix(X_sample, feature_names=list(X_sample.columns))
    try:
        shap_vals = _explainer.shap_values(dmat)
        return -shap_vals, X_sample, race_sample
    except Exception:
        return None, None, None


if DATA_OK and not DEMO:
    shap_vals, X_sample, race_sample = compute_global_shap(val_data, pipeline, explainer, xgb_model)
    SHAP_OK = shap_vals is not None
else:
    SHAP_OK = False
    st.info("**Modo demo** — Importancias SHAP simuladas para ilustración.", icon="ℹ️")

# ─── IMPORTANCIA GLOBAL ───────────────────────────────────────────────────────
st.markdown("---")
st.markdown("### Importancia global (|SHAP| medio)")

if SHAP_OK:
    mean_abs = np.abs(shap_vals).mean(axis=0)
    feat_names = list(X_sample.columns)
    top_idx = np.argsort(mean_abs)[::-1][:15]
    top_labs = [get_label(feat_names[i]) for i in top_idx]
    top_vals = mean_abs[top_idx]
else:
    top_labs = ["Índice Sorror", "KPS basal", "DRI", "HLA match 10 loci", "Edad al trasplante (años)", "Año del HCT", "Citogenética"]
    top_vals = [0.18, 0.17, 0.15, 0.14, 0.13, 0.12, 0.10]

# Definición de Dominios Clínicos usando la paleta centralizada
CLINICAL_DOMAINS = {
    "Enfermedad": {"color": DOMAIN_COLORS["Enfermedad"], "keywords": ["DRI", "Citogen", "ERM", "Enfermedad"]},
    "Paciente/Estado": {"color": DOMAIN_COLORS["Paciente/Estado"], "keywords": ["Sorror", "KPS", "Edad"]},
    "Genética/HLA": {"color": DOMAIN_COLORS["Genética/HLA"], "keywords": ["HLA", "match"]},
    "Procedimiento/Donante": {"color": DOMAIN_COLORS["Procedimiento"], "keywords": []} 
}

def get_domain(label):
    for domain, config in CLINICAL_DOMAINS.items():
        if any(k in label for k in config["keywords"]):
            return domain
    return "Procedimiento/Donante"

# Preparar datos para el gráfico con leyenda
df_plot = pd.DataFrame({
    "Variable": top_labs,
    "Importancia": top_vals,
    "Dominio": [get_domain(lbl) for lbl in top_labs]
}).sort_values("Importancia", ascending=True)

# Construir gráfico con leyenda usando trace por dominio
fig_imp = go.Figure()

for domain, config in CLINICAL_DOMAINS.items():
    df_domain = df_plot[df_plot["Dominio"] == domain]
    if not df_domain.empty:
        fig_imp.add_trace(go.Bar(
            x=df_domain["Importancia"],
            y=df_domain["Variable"],
            name=domain,
            orientation='h',
            marker_color=config["color"],
            opacity=0.85,
            hovertemplate="<b>%{y}</b><br>Dominio: " + domain + "<br>|SHAP|: %{x:.4f}<extra></extra>"
        ))

fig_imp.update_layout(
    title="<b>Top 15 Variables por Importancia Clínica Media</b>",
    xaxis_title="|SHAP| medio (Magnitud del impacto)",
    legend_title="Dominios Clínicos",
    height=600,
    margin=dict(l=20, r=20, t=60, b=40),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    yaxis=dict(categoryorder='total ascending')
)

st.plotly_chart(fig_imp, use_container_width=True)

st.caption("""
**Nota sobre dominios clínicos** 

Los colores agrupan variables según su naturaleza: 

🔴 **Enfermedad**: factores tumorales intrínsecos. 

🔵 **Paciente**: estado basal y comorbilidades. 

🟣 **Genética**: compatibilidad HLA. 

🟠 **Procedimiento**: factores externos al paciente y donante.
""")

# ─── HEATMAP POR RAZA ─────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("### Importancia SHAP por grupo racial")

if SHAP_OK:
    top10_idx = np.argsort(np.abs(shap_vals).mean(axis=0))[::-1][:10]
    top10_labs = [get_label(list(X_sample.columns)[i]) for i in top10_idx]
    matrix = np.zeros((len(RACE_ORDER), 10))
    for i, race in enumerate(RACE_ORDER):
        mask = race_sample == race
        if mask.any():
            matrix[i] = np.abs(shap_vals[mask][:, top10_idx]).mean(axis=0)
else:
    top10_labs = top_labs[:10]
    matrix = np.random.uniform(0.05, 0.2, (len(RACE_ORDER), 10))

fig_heat = px.imshow(
    matrix, x=top10_labs, y=RACE_ORDER,
    color_continuous_scale="YlOrRd",
    labels=dict(color="|SHAP| medio"),
    title="<b>Distribución de la irtancia predictiva por raza</b>"
)
fig_heat.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=450)
st.plotly_chart(fig_heat, use_container_width=True)

# ─── DEPENDENCE PLOT ──────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("### Perfil de dependencia (efecto marginal)")
st.caption("Visualización de cómo varía el riesgo (%) en función de una variable individual. Los puntos están coloreados por grupo racial.")

# Selector de variables dinámico basado en LABEL_MAP y variables disponibles
dep_vars = {v: k for k, v in LABEL_MAP.items() if k in (X_sample.columns if SHAP_OK else [])}
# Ordenamos alfabéticamente para facilitar la búsqueda
sorted_labels = sorted(list(dep_vars.keys())) if dep_vars else ["Edad al trasplante (años)", "KPS basal (40–100)", "Índice Sorror (0–10)", "Año del HCT"]
init_label = "Edad al trasplante (años)"
init_idx = sorted_labels.index(init_label) if init_label in sorted_labels else 0
sel_label = st.selectbox("Selecciona variable Clínica para analizar:", sorted_labels, index=init_idx)

if SHAP_OK:
    v_col = dep_vars[sel_label]
    v_idx = list(X_sample.columns).index(v_col)
    
    x_vals = X_sample[v_col].values
    y_vals = shap_vals[:, v_idx]

    fig_dep = px.scatter(
        x=x_vals, y=y_vals,
        color=race_sample, color_discrete_map=RACE_PALETTE,
        opacity=0.45, template="plotly_white",
        title=f"<b>Efecto Marginal de {sel_label} en el Riesgo Predicho</b>",
        labels={'x': sel_label, 'y': 'Contribución SHAP (Riesgo Relativo)'}
    )
    
    # Línea de tendencia LOWESS (Solo para variables continuas)
    try:
        mask = (~np.isnan(x_vals)) & (~np.isnan(y_vals))
        unique_vals = len(np.unique(x_vals[mask]))
        
        # Rigor académico: no dibujar tendencias en variables con pocos niveles (categóricas/binarias)
        if mask.any() and unique_vals > 10:
            lowess = sm.nonparametric.lowess
            z = lowess(y_vals[mask], x_vals[mask], frac=0.4)
            
            fig_dep.add_trace(go.Scatter(
                x=z[:, 0], y=z[:, 1],
                mode='lines',
                name='Tendencia Media (LOWESS)',
                line=dict(color='black', width=3),
                hoverinfo='skip'
            ))
    except: pass 

    fig_dep.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.7)
    fig_dep.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        height=500,
        legend_title="Grupo Racial",
        legend=dict(orientation="h", yanchor="bottom", y=-0.35, xanchor="center", x=0.5)
    )
    st.plotly_chart(fig_dep, use_container_width=True)
    
    st.markdown(f"""
    **Interpretación académica:** La línea negra representa la **tendencia media (suavizado LOWESS)**. 
    Permite visualizar si el efecto es lineal o si existen "umbrales" críticos (ej. a partir de qué edad o puntuación Sorror el riesgo aumenta drásticamente).
    """)
else:
    st.info("Gráfico de dependencia interactivo disponible con datos SHAP reales.")
