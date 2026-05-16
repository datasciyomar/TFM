"""
schema.py
─────────
Esquemas de validación de datos (Pydantic) para asegurar entradas correctas.
"""

from typing import Optional
from pydantic import BaseModel, Field


class PatientData(BaseModel):
    age_at_hct: float = Field(
        ..., ge=0.0, le=90.0, description="Edad al trasplante (años)"
    )
    karnofsky_score: float = Field(..., ge=40, le=100, description="KPS basal")
    comorbidity_score: float = Field(..., ge=0, le=20, description="Índice Sorror")
    race_group: str

    prim_disease_hct: str
    dri_score: str
    cyto_score: str
    mrd_hct: str

    donor_age: float = Field(..., ge=0.0, le=90.0)
    donor_related: str
    graft_type: str
    conditioning_intensity: str
    hla_high_res_10: float = Field(..., ge=0, le=10)
    cmv_status: str
    tbi_status: str
    year_hct: int = Field(..., ge=1990, le=2030)
    in_vivo_tcd: str
    sex_match: str

    # Opcionales o fijos que el modelo llena tras bambalinas
    diabetes: str = "No"
    obesity: str = "No"
    cardiac: str = "No"
    arrhythmia: str = "No"
    renal_issue: str = "No"
    pulm_severe: str = "No"
    pulm_moderate: str = "No"
    hepatic_severe: str = "No"
    hepatic_mild: str = "No"
    peptic_ulcer: str = "No"
    rheum_issue: str = "No"
    psych_disturb: str = "No"
    prior_tumor: str = "No"
    vent_hist: str = "No"
    tce_match: Optional[str] = None
    tce_div_match: Optional[str] = None
    tce_imm_match: Optional[str] = None
    rituximab: str = "No"
    melphalan_dose: str = "N/A, Mel not given"
    ethnicity: str = "Not Hispanic or Latino"
    cyto_score_detail: Optional[str] = None

    def to_dict(self) -> dict:
        return self.model_dump()
