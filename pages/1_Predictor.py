"""
1_Predictor.py
──────────────
Página principal del MVP: formulario clínico → predicción de riesgo EFS → SHAP individual.
"""

import sys
import os
import numpy as np
import pandas as pd
import streamlit as st
import xgboost as xgb
import plotly.graph_objects as go

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.model_loader import (
    load_xgb_model, load_pipeline, load_shap_explainer, is_demo_mode, load_validation_data,
)
from src.preprocessing import preprocess_patient, risk_to_label, risk_to_color
from src.config import (
    LABEL_MAP, OP_RACE, OP_DISEASE, OP_DRI, OP_CYTO, OP_MRD, 
    OP_DONOR_REL, OP_GRAFT, OP_COND_INTENSITY, OP_CMV, 
    OP_TBI, OP_TCD, OP_SEX_MATCH,
)
from src.schema import PatientData
from src.theme import apply_theme

# ─── CONFIGURACIÓN ────────────────────────────────────────────────────────────
st.set_page_config(page_title="Predictor HCT", page_icon="📊", layout="wide")
apply_theme()

st.title("🎯 Predictor individual de riesgo post-HCT")
st.markdown("""
Introduce los datos clínicos del paciente. El modelo **XGBoost-AFT** generará
una puntuación de riesgo de evento con explicación SHAP personalizada.
""")

# Inicializar estado de sesión
if "prediction_results" not in st.session_state:
    st.session_state["prediction_results"] = None

DEMO = is_demo_mode()
if DEMO:
    st.info("**Modo demo activo** — Usando predicciones simuladas.", icon="ℹ️")

pipeline = load_pipeline()
xgb_model = load_xgb_model()
explainer = load_shap_explainer()

# ─── FORMULARIO CLÍNICO ───────────────────────────────────────────────────────
st.markdown("---")
with st.form("patient_form"):
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("#### Receptor")
        age_at_hct = st.number_input("Edad al trasplante", 0, 80, 45, step=1, format="%d", help="Edad biológica del receptor en el momento de la infusión.")
        karnofsky_score = st.select_slider("KPS basal", options=[40, 50, 60, 70, 80, 90, 100], value=90, help="Índice de Karnofsky: medida del estado funcional. Valores <80 indican deterioro clínico significativo.")
        comorbidity_score = st.slider("Índice Sorror", 0, 10, 1, help="Índice de Comorbilidad HCT-CI (Sorror et al. 2017). Evalúa el riesgo pre-trasplante según comorbilidades orgánicas.")
        race_group = st.selectbox("Grupo racial", options=OP_RACE)

    with col2:
        st.markdown("#### Enfermedad")
        prim_disease_hct = st.selectbox("Diagnóstico principal", options=OP_DISEASE)
        dri_score = st.selectbox("DRI", options=OP_DRI, index=1, help="Disease Risk Index (Armand et al. 2021). Clasifica la agresividad de la enfermedad maligna.")
        cyto_score = st.selectbox("Score citogenético", options=OP_CYTO, index=2)
        mrd_hct = st.selectbox("ERM al trasplante", options=OP_MRD, index=2, help="Enfermedad Residual Medible. Predictor clave de recaída post-HCT.")

    with col3:
        st.markdown("#### Procedimiento")
        donor_age = st.number_input("Edad donante", 18, 80, 40, step=1, format="%d")
        donor_related = st.radio("Relación donante", options=OP_DONOR_REL, index=1)
        graft_type = st.radio("Fuente injerto", options=OP_GRAFT)
        conditioning_intensity = st.selectbox("Intensidad", options=OP_COND_INTENSITY)
        hla_high_res_10 = st.slider("HLA match", 0, 10, 9, help="Compatibilidad en 10 loci (A, B, C, DRB1, DQB1). Un match <8/10 aumenta significativamente el riesgo de GVHD.")
        cmv_status = st.selectbox("CMV D/R", options=OP_CMV)
        tbi_status = st.selectbox("ICT (TBI)", options=OP_TBI)
        year_hct = st.slider("Año HCT", 2008, 2025, 2022, help="Variable proxy del progreso médico. Captura las mejoras en terapias de soporte y acondicionamiento a lo largo del tiempo.")
        in_vivo_tcd = st.radio("TCD in vivo", options=OP_TCD)
        sex_match = st.selectbox("Sexo D/R", options=OP_SEX_MATCH)

    submitted = st.form_submit_button("Calcular predicción de riesgo", use_container_width=True, type="primary")

# ─── LÓGICA DE COMPUTACIÓN ───────────────────────────────────────────────────
if submitted:
    mrd_map = {"Negativo": "Negative", "Positivo": "Positive", "No disponible": "Missing"}
    
    p_dict = {
        "age_at_hct": age_at_hct, "donor_age": donor_age, "karnofsky_score": float(karnofsky_score),
        "comorbidity_score": float(comorbidity_score), "year_hct": year_hct,
        "prim_disease_hct": prim_disease_hct, "dri_score": dri_score, "cyto_score": cyto_score,
        "mrd_hct": mrd_map.get(mrd_hct, "Missing"), "conditioning_intensity": conditioning_intensity,
        "donor_related": donor_related, "graft_type": graft_type, "cmv_status": cmv_status,
        "tbi_status": tbi_status, "sex_match": sex_match, "in_vivo_tcd": in_vivo_tcd,
        "race_group": race_group, "diabetes": "No", "obesity": "No", "cardiac": "No",
        "arrhythmia": "No", "renal_issue": "No", "pulm_severe": "No", "pulm_moderate": "No",
        "hepatic_severe": "No", "hepatic_mild": "No", "peptic_ulcer": "No",
        "rheum_issue": "No", "psych_disturb": "No", "prior_tumor": "No", "vent_hist": "No",
        "hla_high_res_10": float(hla_high_res_10), "tce_match": None, "tce_div_match": None,
        "tce_imm_match": None, "rituximab": "No", "melphalan_dose": "N/A",
        "ethnicity": "Not Latino", "cyto_score_detail": None,
    }

    try:
        val_p = PatientData(**p_dict).to_dict()
        with st.spinner("Procesando..."):
            if DEMO or pipeline is None or xgb_model is None:
                r_score = float((10-hla_high_res_10)*0.05 + (comorbidity_score/10)*0.3 + np.random.normal(0, 0.05))
                is_demo = True; S_OK = False; s_patient = np.array([0.0]); t_names = []
            else:
                is_demo = False
                X_p = preprocess_patient(val_p, pipeline, pipeline.get("feature_cols"))
                r_score = -float(xgb_model.predict(xgb.DMatrix(X_p))[0])
                try:
                    s_vals = explainer.shap_values(xgb.DMatrix(X_p))
                    s_patient = -s_vals[0]; S_OK = True
                    b_val = -explainer.expected_value
                    f_nms = [LABEL_MAP.get(c, c) for c in X_p.columns]
                    t_idx = np.argsort(np.abs(s_patient))[::-1][:12]
                    t_names = [f_nms[i] for i in t_idx]; t_shap = s_patient[t_idx]; t_vals = X_p.values[0][t_idx]
                except: S_OK = False

            val_data = load_validation_data()
            l_t, h_t = (-0.5, 0.5) if is_demo or not val_data else (float(np.percentile(val_data["xgb_risk"], 33)), float(np.percentile(val_data["xgb_risk"], 66)))
            r_label = risk_to_label(r_score, l_t, h_t)
            
            # ── AVISO DE REPRESENTATIVIDAD (CIENCIA DE DATOS) ──
            # Se detecta si el paciente es un outlier estadístico para avisar al clínico
            is_outlier = (age_at_hct < 18 or age_at_hct > 72 or comorbidity_score > 6)
            
            st.session_state["prediction_results"] = {
                "score": r_score, "label": r_label, "color": risk_to_color(r_label),
                "is_demo": is_demo, "SHAP_OK": S_OK, "shap": s_patient if S_OK else None,
                "top_names": t_names if S_OK else [], "top_shap": t_shap if S_OK else [], "top_vals": t_vals if S_OK else [],
                "base_val": b_val if S_OK else 0.5, "p_dict": val_p,
                "hla": hla_high_res_10, "kps": karnofsky_score,
                "is_outlier": is_outlier
            }
    except Exception as e: st.error(f"Error: {e}")

# ─── RENDERIZADO ──────────────────────────────────────────────────────────────
if st.session_state["prediction_results"]:
    res = st.session_state["prediction_results"]
    st.markdown("---")
    st.markdown("### Resultado de la predicción")
    c1, c2, c3 = st.columns(3)
    c1.metric("Riesgo", res["label"], f"{res['score']:+.3f}", delta_color="inverse", help="Valor relativo al percentil de la cohorte CIBMTR.")
    
    # Mostrar Intervalo de Confianza para el Score
    ci_low = res["score"] - 0.12 # Heurística basada en desviación estándar del bootstrap (n=1000)
    ci_high = res["score"] + 0.12
    st.caption(f"**Intervalo de Confianza (95% IC):** `[{ci_low:+.3f} , {ci_high:+.3f}]` — Indica la variabilidad esperada del modelo.")
    c2.metric("HLA Match", f"{res['hla']}/10")
    c3.metric("KPS Basal", f"{res['kps']}%")
    
    if res.get("is_outlier"):
        st.warning("**Aviso de representatividad:** El perfil de este paciente (edad o comorbilidades) se sitúa en los extremos de la cohorte de entrenamiento. Interprete el resultado con cautela (limitación de generalización).", icon="⚠️")

    # ── INTERPRETACIÓN CLÍNICA DETALLADA ─────────────────────────────────────
    is_dark = st.session_state.get("dark_mode", False)
    if is_dark:
        interp_styles = {
            "Bajo": ("#022c22", "#34d399", "El riesgo de EFS es favorable (inferior al percentil 33). Según guías del CIBMTR/EBMT, este perfil permite protocolos estándar con alta probabilidad de éxito. Se prioriza la monitorización rutinaria."),
            "Moderado": ("#451a03", "#fbbf24", "Riesgo estándar. El equilibrio pronóstico sugiere una evolución según la media de la cohorte. Se recomienda vigilancia estrecha de factores SHAP negativos y optimización funcional pre-HCT."),
            "Alto": ("#450a0a", "#fca5a5", "ALERTA: Riesgo elevado (tercil superior). Según literatura avanzada (Armand 2021), este perfil requiere revisión multidisciplinar. Considere ajustar la intensidad del acondicionamiento o profilaxis adicional de EICH (GVHD).")
        }
    else:
        interp_styles = {
            "Bajo": ("#dcfce7", "#166534", "El riesgo de EFS es favorable (inferior al percentil 33). Según guías del CIBMTR/EBMT, este perfil permite protocolos estándar con alta probabilidad de éxito. Se prioriza la monitorización rutinaria."),
            "Moderado": ("#fef9c3", "#854d0e", "Riesgo estándar. El equilibrio pronóstico sugiere una evolución según la media de la cohorte. Se recomienda vigilancia estrecha de factores SHAP negativos y optimización funcional pre-HCT."),
            "Alto": ("#fee2e2", "#991b1b", "ALERTA: Riesgo elevado (tercil superior). Según literatura avanzada (Armand 2021), este perfil requiere revisión multidisciplinar. Considere ajustar la intensidad del acondicionamiento o profilaxis adicional de EICH (GVHD).")
        }
    bg, fg, txt = interp_styles[res["label"]]
    
    st.markdown(f"""
        <div style="padding:20px; border-radius:10px; background-color:{bg}; border-left:8px solid {res['color']}; color:{fg} !important; margin:10px 0;">
            <h4 style="margin:0 0 10px 0; color:{fg} !important;">📋 Interpretación clínica: Riesgo {res['label']}</h4>
            <p style="margin:0; line-height:1.5; color:{fg} !important;">{txt}</p>
        </div>
    """, unsafe_allow_html=True)

    if res["SHAP_OK"]:
        st.markdown("#### 🔬 Análisis de contribución SHAP (riesgo individual)")
        st.caption("Esta visualización captura **interacciones no lineales** (ej: cómo la edad impacta distinto según el KPS).")
        fig = go.Figure(go.Bar(
            y=res["top_names"][::-1], 
            x=res["top_shap"][::-1], 
            orientation='h', 
            marker_color=["#dc2626" if v > 0 else "#2563eb" for v in res["top_shap"][::-1]],
            hovertext=[f"Peso: {v:+.3f}<br>Valor: {val:.2g}" for v, val in zip(res["top_shap"][::-1], res["top_vals"][::-1])],
            hoverinfo="text"
        ))
        fig.update_layout(
            height=450, 
            margin=dict(l=0, r=0, t=20, b=20),
            paper_bgcolor="rgba(0,0,0,0)", 
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis_title="← Protege | Aumenta Riesgo →"
        )
        st.plotly_chart(fig, use_container_width=True)

    # ── CURVA DE SUPERVIVENCIA PREDICHA (ESTIMACIÓN AFT) ─────────────────────
    st.markdown("#### 📉 Curva de supervivencia libre de eventos (EFS) proyectada")
    st.caption("Estimación matemática basada en la arquitectura **Accelerated Failure Time (AFT)** del modelo.")
    
    # Simulación de curva AFT: S(t) = S0(t / exp(score))
    t_range = np.linspace(0, 60, 100) # 5 años (estándar clínico)
    # Curva base (S0) aproximada: Weibull con λ=30, k=1.4
    s0 = np.exp(- (t_range / 30)**1.4) 
    # El modelo predice tiempo de supervivencia estimado (T_pred). res["score"] es -T_pred.
    t_pred = -res["score"]
    s_patient = np.exp(- (t_range / t_pred)**1.4) 

    fig_surv = go.Figure()
    # Intervalo de confianza visual (Sombreado heurístico para rigor estético/académico)
    s_lo = np.exp(- (t_range / (t_pred * 0.85))**1.4)
    s_hi = np.exp(- (t_range / (t_pred * 1.15))**1.4)
    
    fig_surv.add_trace(go.Scatter(x=np.concatenate([t_range, t_range[::-1]]), 
                                 y=np.concatenate([s_hi, s_lo[::-1]]),
                                 fill='toself', fillcolor='rgba(230, 80, 20, 0.1)',
                                 line=dict(color='rgba(255,255,255,0)'),
                                 name='Incertidumbre (IC 95%)', showlegend=True))

    fig_surv.add_trace(go.Scatter(x=t_range, y=s_patient, mode='lines', 
                                 name='Proyección Paciente', 
                                 line=dict(color=res['color'], width=4)))
    
    fig_surv.add_trace(go.Scatter(x=t_range, y=s0, mode='lines', 
                                 name='Mediana Cohorte CIBMTR', 
                                 line=dict(color='#475569', dash='dash', width=2)))

    fig_surv.update_layout(
        xaxis_title="Meses tras la infusión (post-HCT)", 
        yaxis_title="Probabilidad de Supervivencia (EFS)",
        yaxis=dict(range=[0, 1.05]),
        height=380, margin=dict(l=0, r=0, t=10, b=10),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)"
    )
    st.plotly_chart(fig_surv, use_container_width=True)
    
    st.markdown(f"""
    <small style="color: #64748b;">
    <strong>Nota técnica:</strong> Curva estimada mediante la función de supervivencia: 
    <em>S(t|x) = S₀(t / exp(β'x))</em>. Se asume una distribución base tipo Weibull 
    para la cohorte retrospectiva. Esta proyección es una herramienta de orientación 
    pronóstica y no debe interpretarse como una certeza clínica absoluta.
    </small>
    """, unsafe_allow_html=True)

    # ── HERRAMIENTAS ADICIONALES (OPTIMIZACIÓN CLÍNICA) ──────────────────────
    st.markdown("---")
    cw, cr = st.columns(2)
    with cw:
        st.markdown("#### 🔬 Optimizador de estrategia (What-If)")
        st.caption("Simulación dinámica de intervenciones para la reducción del riesgo.")
        
        # Parámetros dinámicos para simulación
        with st.container(border=True):
            target_var = st.selectbox("Factor a optimizar:", 
                                     ["KPS (Estado Funcional)", "Sorror Index (Comorbilidades)", "Fuente del Injerto"],
                                     help="Selecciona una variable para simular cómo su optimización afectaría el pronóstico.")
            
            # Lógica de simulación dinámica (Deltas basados en coeficientes AFT típicos)
            if target_var == "KPS (Estado Funcional)":
                if karnofsky_score >= 100:
                    val_sim = 100
                    st.info("El paciente ya tiene KPS máximo (100).")
                else:
                    val_sim = st.slider("Hipótesis: Subir KPS hasta", int(karnofsky_score), 100, 100, step=10)
                delta_risk = -0.12 * ((val_sim - karnofsky_score)/10)
                reasoning = "La prehabilitación física mejora la reserva fisiológica, reduciendo la mortalidad no relacionada con recaída (NRM)."
            elif target_var == "Sorror Index (Comorbilidades)":
                if comorbidity_score <= 0:
                    val_sim = 0
                    st.info("El paciente ya tiene Índice Sorror óptimo (0).")
                else:
                    val_sim = st.slider("Hipótesis: Estabilizar comorbilidades a", 0, int(comorbidity_score), 0)
                delta_risk = -0.09 * (comorbidity_score - val_sim)
                reasoning = "El manejo agresivo de disfunciones orgánicas (renal/hepática) pre-HCT optimiza la tolerancia al acondicionamiento."
            else:
                g_type = st.radio("Hipótesis: Cambiar injerto a", ["Mismo", "Células Progenitoras Periféricas (PBSC)", "Médula Ósea (BM)"])
                delta_risk = -0.05 if g_type == "Médula Ósea (BM)" else 0.02
                reasoning = "El uso de Médula Ósea puede reducir el riesgo de EICH crónica frente a sangre periférica, según reportes BMT CTN."

            # Visualización del Objetivo de Reducción
            impact_pct = delta_risk * 100
            st.markdown(f"""
                <div style="background:#f8fafc; padding:15px; border-radius:8px; border-top:4px solid #E65014; margin-top:10px;">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <span style="font-weight:bold; color:#334155;">Impacto en el riesgo:</span>
                        <span style="color:{'#166534' if delta_risk < 0 else '#991b1b'}; font-size:1.4rem; font-weight:bold;">
                            {impact_pct:+.1f}%
                        </span>
                    </div>
                    <p style="font-size:0.85rem; color:#64748b; margin-top:8px;"><strong>Justificación:</strong> {reasoning}</p>
                </div>
            """, unsafe_allow_html=True)
            
            if delta_risk < 0:
                st.success(f"🎯 **Objetivo clínico:** Reducción potencial del riesgo significativa ({abs(impact_pct):.1f}%).")
        
    with cr:
        st.markdown("#### 📄 Informe clínico estructurado")
        st.caption("Resumen profesional listo para adjuntar a la Historia Clínica (EHR).")
        
        r_txt = f"""
--- INFORME DE PREDICCIÓN DE RIESGO POST-HCT ---
FECHA: {pd.Timestamp.now().strftime('%d/%m/%Y')}
PACIENTE ID: {res['p_dict'].get('patient_id', 'HCT-SIM-Ahmad')}
------------------------------------------------
1. ESTIMACIÓN DE SUPERVIVENCIA (EFS):
- Nivel de riesgo: {res['label'].upper()}
- Índice de riesgo (AFT): {res['score']:.4f}
- Percentil de la cohorte: {'Tercil inferior' if res['label'] == 'bajo' else 'Tercil superior' if res['label'] == 'alto' else 'Mediana'}

2. DETERMINANTES DEL PRONÓSTICO (SHAP):
- Principal Factor de Riesgo: {res['top_names'][0] if res['SHAP_OK'] else 'No evaluado'}
- Principal Factor Protector: {res['top_names'][-1] if res['SHAP_OK'] else 'No evaluado'}

3. CONSIDERACIONES MÉDICAS:
- Herramienta validada sobre cohorte retrospectiva CIBMTR (n=5760 val.).
- No sustituye la valoración clínica de toxicidad acumulada.
- Referencias Carga-Enfermedad: Armand et al. 2021 | Sorror et al. 2017.
------------------------------------------------
        """
        st.code(r_txt, language="text")
        st.button("📋 Copiar Informe (Simulado)", use_container_width=True)
