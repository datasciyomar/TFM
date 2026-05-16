import streamlit as st

st.set_page_config(page_title="Diccionario de datos", page_icon="📖", layout="wide")

from src.theme import apply_theme
apply_theme()

st.title("📖 Diccionario de datos clínicos")
st.markdown("""
Este diccionario contiene el mapeo exacto de los atributos clínicos y categóricos configurados en el MVP y transformados por el pipeline de validación, garantizando la trazabilidad de los datos hacia el modelo **XGBoost-AFT**.
""")

st.markdown("---")

st.markdown("""
| Atributo Clínico | Variable Interna | Valores Posibles o Tipo Numérico |
|---|---|---|
| **Edad del Receptor** | `age_at_hct` | Numérica Continua (0.0 – 80.0 años) |
| **KPS Basal** | `karnofsky_score` | Numérica Discreta (40, 50, 60, 70, 80, 90, 100) |
| **Índice Sorror HCT-CI** | `comorbidity_score` | Numérica Discreta (0 – 10) |
| **Diagnóstico Primario** | `prim_disease_hct` | AML, ALL, MDS, MPN, NHL, Solid tumor... *(18 clasificaciones)* |
| **Índice de Riesgo (DRI)** | `dri_score` | Low, Intermediate, High, Very high, N/A, TBD |
| **Puntuación citogenética** | `cyto_score` | Favorable, Normal, Intermediate, Poor, TBD, Not tested |
| **Enfermedad residual mínima**| `mrd_hct` | Negativo, Positivo, No disponible |
| **Compatibilidad HLA (10 alelos)** | `hla_high_res_10` | Numérica Discreta (0 – 10) |
| **Edad del Donante** | `donor_age` | Numérica Continua (18.0 – 80.0 años) |
| **Relación Donante-Receptor** | `donor_related` | Related, Unrelated |
| **Fuente de Células (Injerto)** | `graft_type` | Peripheral blood, Bone marrow |
| **Intensidad del Acondicionamiento**| `conditioning_intensity`| MAC, RIC, NMA |
| **Seroestado CMV (D/R)** | `cmv_status` | +/+, +/-, -/+, -/- |
| **Irradiación corporal total** | `tbi_status` | No TBI, TBI + Cy, >cGy, <=cGy |
| **Depleción T in vivo (ATG)** | `in_vivo_tcd` | Yes, No |
| **Compatibilidad de sexo (D/R)**| `sex_match` | M-M, F-F, M-F, F-M |
""")
    
st.markdown("""
<div class="clinical-warning">
<strong>Aclaración metodológica de equidad:</strong><br>
La variable <code>race_group</code> (grupos raciales) es solicitada por el formulario, pero 
<strong>no es utilizada</strong> como predictor causal explícito (Feature) por los árboles de decisión en inferencia. Se almacena y se incluye en el vector estricta y exclusivamente para posibilitar la <strong>evaluación matemática de sesgos algorítmicos</strong> post-hoc en la pestaña de Equidad.
</div>
""", unsafe_allow_html=True)

st.markdown("---")
st.markdown("### 📚 Referencias")
st.markdown("""
Para garantizar la validez científica del MVP, se han integrado escalas y metodologías validadas en la literatura hematológica reciente (2016–2024):

1. 
2. 
3. 
4. 
5. 
6. 
7. 
""")

st.markdown("---")
st.markdown("### Limitaciones y trabajo futuro")
st.info("""
Para una defensa de TFM rigurosa, se deben considerar las siguientes limitaciones inherentes al MVP actual:
1. **Naturaleza retrospectiva:** Los datos provienen de registros históricos de la cohorte CIBMTR. La utilidad real del modelo debe ser validada en ensayos prospectivos.
2. **Ausencia de validación externa:** El rendimiento se basa en un conjunto de validación interno. La generalización a otras poblaciones requiere una re-calibración local.
3. **Determinantes no medidos:** Variables como el cumplimiento terapéutico post-trasplante o el soporte nutricional específico no están capturadas en el modelo original.
4. **Dinamicidad del riesgo:** El modelo proporciona una foto fija pre-HCT. El riesgo evoluciona dinámicamente según la aparición de complicaciones como la EICH aguda.
""")
