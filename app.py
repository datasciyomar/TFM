"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  MVP CLÍNICO — Predicción de Supervivencia Post-HCT y Equidad Racial        ║
║  TFM · Máster en Epidemiología y Salud Pública · VIU 2024-25                ║
╚══════════════════════════════════════════════════════════════════════════════╝

Punto de entrada de la aplicación Streamlit.
Ejecutar con: streamlit run app.py

Estructura de páginas:
  app.py                  → bienvenida + navegación
  pages/1_Predictor.py    → formulario clínico + predicción individual
  pages/2_Equidad.py      → análisis de equidad por grupo racial
  pages/3_SHAP.py         → interpretabilidad (waterfall + beeswarm)
"""

import os
import streamlit as st

# ─── CONFIGURACIÓN GLOBAL DE PÁGINA ──────────────────────────────────────────
st.set_page_config(
    page_title="HCT Survival Predictor",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get help": None,
        "Report a bug": None,
        "About": "TFM Epidemiología VIU 2025-26 · Uso exclusivamente académico y de investigación.",
    },
)

# ─── ESTILOS GLOBALES ─────────────────────────────────────────────────────────


from src.theme import apply_theme
apply_theme()

# ─── SIDEBAR ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### HCT Survival MVP")
    st.markdown("**Versión:** 1.0.0 · Uso académico")
    st.markdown("---")
    st.markdown(
        """
    <div class='clinical-warning'>
    <strong>Aviso</strong><br>
    Esta herramienta es un prototipo académico. No debe usarse para tomar
    decisiones clínicas reales sin validación prospectiva independiente.
    </div>
    """,
        unsafe_allow_html=True,
    )

# ─── PÁGINA DE BIENVENIDA ─────────────────────────────────────────────────────
col_title, col_logo = st.columns([3, 1])

with col_title:
    st.markdown(
        """
        <div style="border: 3px solid #E65014; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
            <h1 style="margin-top: 0; padding-top: 0; margin-bottom: 10px;">🩺 Predictor de supervivencia post-trasplante hematopoyético</h1>
            <h5 style="margin-bottom: 5px; color: #E65014;">MVP Clínico · TFM Epidemiología y Salud Pública · VIU 2025-26</h5>
            <p style="margin: 0; opacity: 0.85; font-size: 0.95em;"><strong>Estudiante:</strong> Ahmad Yaman Omar Dallal</p>
            <p style="margin: 0; opacity: 0.85; font-size: 0.95em;"><strong>Tutora:</strong> Susana Vila Vicent</p>
        </div>
        """,
        unsafe_allow_html=True
    )

with col_logo:
    st.image("https://upload.wikimedia.org/wikipedia/commons/f/f8/Logo_VIU.png", use_column_width=True)

st.markdown("---")

col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("""
    ### Bienvenido/a al MVP del TFM

    Esta aplicación implementa los modelos desarrollados en el TFM para la
    **predicción del Event-Free Survival (EFS)** post-trasplante hematopoyético (HCT),
    con análisis integrado de equidad algorítmica entre grupos raciales.

    #### Qué puedes hacer aquí

    **📊 Predictor individual** — Introduce los datos clínicos de un paciente
    y obtén la predicción de riesgo del modelo XGBoost-AFT, con explicación
    SHAP personalizada para ese caso.

    **⚖️ Análisis de equidad** — Visualiza el C-index estratificado por grupo racial
    sobre el conjunto de validación completo, con intervalos de confianza bootstrap.

    **🔍 Interpretabilidad SHAP** — Explora la importancia global de las variables
    y los gráficos de dependencia. Compara la importancia SHAP entre grupos raciales.

    ---
    #### Modelo principal: XGBoost-AFT
    | Métrica | Valor |
    |---|---|
    | C-index global (val.) | 0.681 |
    | C-index estratificado (val.) | 0.668 |
    | Disparidad racial (max-min) | 0.051 |
    | N entrenamiento | 23.040 |
    | N validación | 5.760 |
    """)

with col2:
    st.markdown("### Cohorte CIBMTR")
    st.metric("Pacientes totales", "28.800")
    st.metric("Tasa de eventos (EFS)", "53,9%")
    st.metric("Mediana seguimiento", "9,8 meses")
    st.metric("Período", "2008–2020")
    st.metric("Grupos raciales", "6 (balanceados)")

    st.markdown("---")
    st.markdown("**Fuente de datos**")
    st.markdown("""
    [CIBMTR Kaggle Competition](https://www.kaggle.com/competitions/equity-post-HCT-survival-predictions)
    Equity in Post-HCT Survival Predictions (2024)
    """)

st.markdown("---")
st.markdown(
    """
<small style='color: #888;'>
<strong>Nota:</strong> Los resultados de esta herramienta reflejan
patrones estadísticos aprendidos de datos históricos. Los valores SHAP cuantifican
la contribución de cada variable a la <em>predicción del modelo</em>, no efectos causales.
La raza se incluye exclusivamente como variable de estratificación para el análisis de
equidad algorítmica, no como predictor clínico del pronóstico individual.
</small>
""",
    unsafe_allow_html=True,
)
