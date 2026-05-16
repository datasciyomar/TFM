"""
config.py
─────────
Configuración estática y diccionarios centralizados para el MVP HCT.
"""

LABEL_MAP = {
    "age_at_hct": "Edad al trasplante (años)",
    "donor_age": "Edad del donante (años)",
    "karnofsky_score": "KPS basal (40–100)",
    "comorbidity_score": "Índice Sorror (0–10)",
    "year_hct": "Año del HCT",
    "hla_high_res_10": "Compatibilidad HLA de alta resolución (0–10)",
    "prim_disease_hct": "Enfermedad primaria",
    "dri_score": "Índice DRI (Riesgo de enfermedad)",
    "conditioning_intensity": "Intensidad de acondicionamiento",
    "donor_related": "Relación donante-receptor",
    "graft_type": "Tipo de injerto",
    "cmv_status": "Seroestado CMV D/R",
    "sex_match": "Compatibilidad de sexo D/R",
    "in_vivo_tcd": "Depleción T in vivo (ATG)",
    "tbi_status": "Irradiación corporal total",
    "cyto_score": "Puntuación citogenética",
    "mrd_hct": "ERM al trasplante",
    "race_group": "Grupo racial (solo para análisis de equidad)",
}

# ─── PALETA DE COLORES (Consistencia Visual) ──────────────────────────────────
# Colores por dominio clínico
DOMAIN_COLORS = {
    "Enfermedad": "#dc2626",     # Rojo: Factores tumorales
    "Paciente/Estado": "#1565C0",# Azul: Factores basales
    "Genética/HLA": "#8E24AA",    # Púrpuma: Compatibilidad
    "Procedimiento": "#F57F17",  # Naranja: Factores externos
}

# Paleta Okabe-Ito (Segura para daltonismo)
RACE_PALETTE = {
    "White": "#0072B2",
    "Black or African-American": "#E69F00",
    "Asian": "#009E73",
    "Native Hawaiian or other Pacific Islander": "#CC79A7",
    "American Indian or Alaska Native": "#D55E00",
    "More than one race": "#56B4E9",
}

# ─── Opciones para Selectores en UI ──────────────────────────────────────────

OP_RACE = [
    "White",
    "Black or African-American",
    "Asian",
    "Native Hawaiian or other Pacific Islander",
    "American Indian or Alaska Native",
    "More than one race",
]

OP_DISEASE = [
    "AML",
    "ALL",
    "MDS",
    "MPN",
    "NHL",
    "IPA",
    "IEA",
    "SAA",
    "IIS",
    "PCD",
    "HIS",
    "AI",
    "IMD",
    "HD",
    "CML",
    "Solid tumor",
    "Other acute leukemia",
    "Other leukemia",
]

OP_DRI = [
    "Low",
    "Intermediate",
    "High",
    "Very high",
    "N/A - non-malignant indication",
    "N/A - pediatric",
    "TBD cytogenetics",
]

OP_CYTO = ["Favorable", "Normal", "Intermediate", "Poor", "TBD", "Not tested"]

OP_MRD = ["Negativo", "Positivo", "No disponible"]

OP_DONOR_REL = ["Related", "Unrelated"]

OP_GRAFT = ["Peripheral blood", "Bone marrow"]

OP_COND_INTENSITY = ["MAC", "RIC", "NMA"]

OP_CMV = ["+/+", "+/-", "-/+", "-/-"]

OP_TBI = ["No TBI", "TBI + Cy +- Other", "TBI +- Other, >cGy", "TBI +- Other, <=cGy"]

OP_TCD = ["No", "Yes"]

OP_SEX_MATCH = ["M-M", "F-F", "M-F", "F-M"]
