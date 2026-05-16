import pytest
import pandas as pd
from src.schema import PatientData
from src.preprocessing import preprocess_patient, risk_to_label


def test_patient_data_validation():
    """Prueba que Pydantic valide correctamente la estructura de datos."""
    valid_data = {
        "age_at_hct": 45.0,
        "karnofsky_score": 90,
        "comorbidity_score": 1,
        "race_group": "White",
        "prim_disease_hct": "AML",
        "dri_score": "Intermediate",
        "cyto_score": "Normal",
        "mrd_hct": "Negative",
        "donor_age": 40.0,
        "donor_related": "Related",
        "graft_type": "Peripheral blood",
        "conditioning_intensity": "MAC",
        "hla_high_res_10": 10.0,
        "cmv_status": "+/+",
        "tbi_status": "No TBI",
        "year_hct": 2022,
        "in_vivo_tcd": "No",
        "sex_match": "M-M",
    }

    # Debe instanciarse sin errores
    patient = PatientData(**valid_data)
    patient_dict = patient.to_dict()

    assert patient_dict["age_at_hct"] == 45.0
    assert patient_dict["diabetes"] == "No"  # Valor por defecto inyectado

    # Probar que falla si falte un campo obligatorio
    invalid_data = valid_data.copy()
    del invalid_data["age_at_hct"]

    with pytest.raises(Exception):
        PatientData(**invalid_data)


def test_risk_to_label():
    """Prueba de que risk_to_label asigne las etiquetas correctas."""
    assert risk_to_label(-1.0, -0.5, 0.5) == "Bajo"
    assert risk_to_label(0.0, -0.5, 0.5) == "Moderado"
    assert risk_to_label(1.0, -0.5, 0.5) == "Alto"


def test_preprocess_patient_demo():
    """Prueba la solidez del motor de preprocesado en modo genérico (sin pipeline)."""
    valid_data = {
        "age_at_hct": 45.0,
        "karnofsky_score": 90,
        "comorbidity_score": 1,
        "race_group": "White",
        "prim_disease_hct": "AML",
        "dri_score": "Intermediate",
        "cyto_score": "Normal",
        "mrd_hct": "Negative",
        "donor_age": 40.0,
        "donor_related": "Related",
        "graft_type": "Peripheral blood",
        "conditioning_intensity": "MAC",
        "hla_high_res_10": 10.0,
        "cmv_status": "+/+",
        "tbi_status": "No TBI",
        "year_hct": 2022,
        "in_vivo_tcd": "No",
        "sex_match": "M-M",
    }
    patient = PatientData(**valid_data)
    patient_dict = patient.to_dict()

    # Preprocesado fallara si hay problemas en los defaults de MNAR o dict
    # Simularemos pipeline objects vacío
    pipeline_objects = {
        "imputation_params": {"medians_num": {"karnofsky_score": 90}, "modes_cat": {}},
        "label_encoders": {},
        "feature_cols": ["age_at_hct", "karnofsky_score"],
    }

    df = preprocess_patient(
        patient_dict, pipeline_objects, feature_cols=["age_at_hct", "karnofsky_score"]
    )

    assert isinstance(df, pd.DataFrame)
    assert len(df) == 1
    assert "age_at_hct" in df.columns
