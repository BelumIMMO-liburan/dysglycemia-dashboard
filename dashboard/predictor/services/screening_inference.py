"""
Stage-1 Non-Laboratory Screening Inference Adapter
Phase D2.3 Implementation — Frozen GAM Integration

Authoritative Service for:
1. Cryptographic artifact integrity verification (SHA256).
2. Cached, read-only loading of frozen Phase-5 GAM and preprocessor.
3. Deterministic semantic-to-model factor encoding.
4. Development-fitted StandardScaler transformation (no new fitting).
5. PyGAM predict_mu inference at frozen threshold 0.1389.
6. Safe typed inference result generation.

GOVERNANCE NOTICE:
This module consumes frozen research artifacts only. It never recalibrates,
refits, or exposes threshold adjustments.
"""

import os
import pickle
import hashlib
import threading
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, Any, List, Optional
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler


# Expected frozen artifact hashes (Canonical Phase-5 baseline)
EXPECTED_GAM_SHA256: str = "204a94ff072ef4f1edecebf5a643738c006bbf010f3817b4bb798d3ea6fef41d"
EXPECTED_PREPROCESSOR_SHA256: str = "6e56a01993a4a6971eb62c82699c49da6f31a3acec2a1169e07862409f42824d"

# Frozen research decision threshold (targeting >=90% development sensitivity)
FROZEN_DECISION_THRESHOLD: float = 0.1389

# Immutable canonical predictor order matching Phase 4/5 evaluation
CANONICAL_PREDICTOR_ORDER: List[str] = [
    "age",
    "sex",
    "bmi",
    "hypertension_history",
    "smoking_history",
    "waist_cm",
    "sedentary_minutes_day",
]

CONTINUOUS_FEATURES: List[str] = ["age", "bmi", "waist_cm", "sedentary_minutes_day"]
CATEGORICAL_FEATURES: List[str] = ["sex", "hypertension_history", "smoking_history"]


class ScreeningInferenceError(Exception):
    """Base exception for all Stage-1 screening inference errors."""
    pass


class InferenceArtifactError(ScreeningInferenceError):
    """Raised when model or preprocessor files are missing, corrupted, or have hash mismatches."""
    pass


ArtifactIntegrityError = InferenceArtifactError


class InferenceDomainError(ScreeningInferenceError):
    """Raised when input parameters fail semantic contract or contain unsupported values."""
    pass


class InferenceExecutionError(ScreeningInferenceError):
    """Raised when preprocessing or GAM inference execution fails."""
    pass


# Aliases for baseline hashes
GAM_MODEL_SHA256 = EXPECTED_GAM_SHA256
PREPROCESSOR_SHA256 = EXPECTED_PREPROCESSOR_SHA256


@dataclass(frozen=True)
class ScreeningInferenceResult:
    """Deterministic, immutable container for screening inference output."""
    probability: float
    referral_recommended: bool
    threshold: float = FROZEN_DECISION_THRESHOLD
    model_name: str = "GAM"
    model_version: str = "Phase-5 GAM (λ=10.0, Splines=10)"
    preprocessor_version: str = "FrozenPreprocessor (Phase-5 StandardScaler)"
    execution_timestamp: str = ""
    formatted_probability: str = ""
    formatted_recommendation: str = ""
    raw_transformed_vector: Optional[List[float]] = None

    @property
    def screening_probability(self) -> float:
        return self.probability

    @property
    def screening_score_pct(self) -> float:
        return self.probability * 100.0

    @property
    def decision_threshold(self) -> float:
        return self.threshold

    @property
    def preliminary_decision(self) -> str:
        return "REFER" if self.referral_recommended else "ROUTINE"

    @property
    def preliminary_recommendation(self) -> str:
        return self.formatted_recommendation


class ScreeningInferenceAdapter:
    """Object-oriented adapter interface providing access to frozen inference service."""
    def verify_integrity(self):
        d = verify_artifact_integrity()
        return d["gam_hash"], d["preprocessor_hash"]

    def predict(self, cleaned_data: Dict[str, Any]) -> ScreeningInferenceResult:
        return predict_screening(cleaned_data)

    @property
    def _gam(self):
        g, _ = load_model_and_preprocessor()
        return g

    @property
    def _preprocessor(self):
        _, p = load_model_and_preprocessor()
        return p


ScreeningInferenceService = ScreeningInferenceAdapter


_ADAPTER_INSTANCE = None


def get_inference_adapter() -> ScreeningInferenceAdapter:
    """Return singleton instance of the ScreeningInferenceAdapter."""
    global _ADAPTER_INSTANCE
    if _ADAPTER_INSTANCE is None:
        _ADAPTER_INSTANCE = ScreeningInferenceAdapter()
    return _ADAPTER_INSTANCE


# Class definition mirroring the frozen Phase-5 script for unpickling
class FrozenPreprocessor:
    """Reconstructed preprocessor class matching the Phase-5 saved artifact."""
    def __init__(self):
        self.features = CANONICAL_PREDICTOR_ORDER.copy()
        self.continuous = CONTINUOUS_FEATURES.copy()
        self.scaler = StandardScaler()
        self.is_fitted = False

    def transform(self, df: pd.DataFrame) -> np.ndarray:
        if not self.is_fitted:
            raise InferenceExecutionError("Preprocessor must be fitted on development data before transform!")
        out = df.copy()
        scaled_cont = self.scaler.transform(out[self.continuous])
        out[self.continuous] = scaled_cont
        return out[self.features].values.astype(np.float32)


class SafePreprocessorUnpickler(pickle.Unpickler):
    """Safe unpickler that resolves '__main__.FrozenPreprocessor' to the local class."""
    def find_class(self, module: str, name: str):
        if name == "FrozenPreprocessor":
            return FrozenPreprocessor
        return super().find_class(module, name)


# Singleton caching storage
_LOAD_LOCK = threading.Lock()
_CACHED_GAM: Optional[Any] = None
_CACHED_PREPROCESSOR: Optional[FrozenPreprocessor] = None


def compute_file_sha256(filepath: Path) -> str:
    """Compute lowercase SHA-256 hash of a file."""
    if not filepath.exists():
        raise InferenceArtifactError(f"Artifact file not found: {filepath.name}")
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest().lower()


def get_artifact_paths() -> Dict[str, Path]:
    """Resolve trusted paths to Phase-5 frozen model artifacts."""
    base_dir = Path(__file__).resolve().parent.parent.parent.parent
    models_dir = base_dir / "nhanes_feasibility_2021_2023" / "models_phase5"
    return {
        "gam": models_dir / "gam_final.pkl",
        "preprocessor": models_dir / "preprocessor.pkl",
    }


def verify_artifact_integrity() -> Dict[str, str]:
    """
    Cryptographically verify that model files match canonical baseline SHA256.
    Fails closed if any hash discrepancy is detected.
    """
    paths = get_artifact_paths()

    gam_hash = compute_file_sha256(paths["gam"])
    if gam_hash != EXPECTED_GAM_SHA256:
        raise InferenceArtifactError(
            f"GAM artifact hash mismatch! Expected {EXPECTED_GAM_SHA256}, got {gam_hash}. Failing closed."
        )

    preproc_hash = compute_file_sha256(paths["preprocessor"])
    if preproc_hash != EXPECTED_PREPROCESSOR_SHA256:
        raise InferenceArtifactError(
            f"Preprocessor artifact hash mismatch! Expected {EXPECTED_PREPROCESSOR_SHA256}, got {preproc_hash}. Failing closed."
        )

    return {
        "gam_hash": gam_hash,
        "preprocessor_hash": preproc_hash,
    }


def load_model_and_preprocessor():
    """
    Load frozen GAM and preprocessor artifacts in a thread-safe, read-only cache.
    Verifies SHA256 integrity before loading.
    """
    global _CACHED_GAM, _CACHED_PREPROCESSOR

    if _CACHED_GAM is not None and _CACHED_PREPROCESSOR is not None:
        return _CACHED_GAM, _CACHED_PREPROCESSOR

    with _LOAD_LOCK:
        if _CACHED_GAM is not None and _CACHED_PREPROCESSOR is not None:
            return _CACHED_GAM, _CACHED_PREPROCESSOR

        verify_artifact_integrity()
        paths = get_artifact_paths()

        try:
            with open(paths["gam"], "rb") as f:
                gam_obj = pickle.load(f)

            with open(paths["preprocessor"], "rb") as f:
                preproc_obj = SafePreprocessorUnpickler(f).load()

            if not getattr(preproc_obj, "is_fitted", False):
                raise InferenceArtifactError("Loaded preprocessor is not fitted!")

            _CACHED_GAM = gam_obj
            _CACHED_PREPROCESSOR = preproc_obj

            return _CACHED_GAM, _CACHED_PREPROCESSOR
        except Exception as e:
            if isinstance(e, InferenceArtifactError):
                raise
            raise InferenceArtifactError(f"Failed to load research artifacts safely: {str(e)}") from e


def encode_and_order_inputs(cleaned_data: Dict[str, Any]) -> pd.DataFrame:
    """
    Validate presence and deterministically encode human semantic values to model features.
    Enforces the immutable canonical predictor order.
    """
    # 1. Assert all 7 required keys exist
    for key in CANONICAL_PREDICTOR_ORDER:
        if key not in cleaned_data:
            raise InferenceDomainError(f"Missing required Stage-1 parameter: '{key}'.")
        val = cleaned_data[key]
        if val is None:
            raise InferenceDomainError(f"Parameter '{key}' cannot be null or empty.")
        if isinstance(val, float) and (np.isnan(val) or np.isinf(val)):
            raise InferenceDomainError(f"Parameter '{key}' contains invalid non-finite value.")

    # 2. Encode categorical variables to frozen factor indicators (1.0 / 0.0)
    # Sex: male -> 1.0, female -> 0.0
    raw_sex = str(cleaned_data["sex"]).strip().lower()
    if raw_sex in ("male", "1", "1.0"):
        sex_encoded = 1.0
    elif raw_sex in ("female", "0", "0.0", "2", "2.0"):
        sex_encoded = 0.0
    else:
        raise InferenceDomainError(f"Unsupported semantic value for sex: '{cleaned_data['sex']}'.")

    # Hypertension: yes -> 1.0, no -> 0.0
    raw_hyp = str(cleaned_data["hypertension_history"]).strip().lower()
    if raw_hyp in ("yes", "1", "1.0"):
        hyp_encoded = 1.0
    elif raw_hyp in ("no", "0", "0.0", "2", "2.0"):
        hyp_encoded = 0.0
    else:
        raise InferenceDomainError(f"Unsupported semantic value for hypertension history: '{cleaned_data['hypertension_history']}'.")

    # Smoking: yes -> 1.0, no -> 0.0
    raw_smk = str(cleaned_data["smoking_history"]).strip().lower()
    if raw_smk in ("yes", "1", "1.0"):
        smk_encoded = 1.0
    elif raw_smk in ("no", "0", "0.0", "2", "2.0"):
        smk_encoded = 0.0
    else:
        raise InferenceDomainError(f"Unsupported semantic value for smoking history: '{cleaned_data['smoking_history']}'.")

    # 3. Numeric conversion and validation
    try:
        age_val = float(cleaned_data["age"])
        bmi_val = float(cleaned_data["bmi"])
        waist_val = float(cleaned_data["waist_cm"])
        sed_val = float(cleaned_data["sedentary_minutes_day"])
    except (ValueError, TypeError) as e:
        raise InferenceDomainError(f"Numeric parameter conversion failure: {str(e)}") from e

    # 4. Construct single-row DataFrame in immutable canonical order
    row_dict = {
        "age": [age_val],
        "sex": [sex_encoded],
        "bmi": [bmi_val],
        "hypertension_history": [hyp_encoded],
        "smoking_history": [smk_encoded],
        "waist_cm": [waist_val],
        "sedentary_minutes_day": [sed_val],
    }
    df = pd.DataFrame(row_dict)[CANONICAL_PREDICTOR_ORDER]

    return df


def predict_screening(cleaned_data: Dict[str, Any]) -> ScreeningInferenceResult:
    """
    Execute end-to-end non-laboratory Stage-1 screening inference.

    Pipeline Steps:
    1. Deterministically encode semantic inputs and enforce canonical ordering.
    2. Retrieve cached frozen GAM and preprocessor (with SHA256 validation).
    3. Transform continuous variables with pre-fitted development StandardScaler.
    4. Call gam.predict_mu() to obtain screening probability in [0, 1].
    5. Evaluate decision rule (prob >= 0.1389) at full precision without rounding.
    6. Return typed ScreeningInferenceResult.
    """
    # 1. Encode and order
    df_input = encode_and_order_inputs(cleaned_data)

    # 2. Retrieve models
    gam_model, preprocessor = load_model_and_preprocessor()

    # 3. Transform features (never fitting)
    try:
        X_trans = preprocessor.transform(df_input)
    except Exception as e:
        raise InferenceExecutionError(f"Preprocessing transformation failure: {str(e)}") from e

    # Assert matrix shape and content
    if X_trans.shape != (1, 7):
        raise InferenceExecutionError(f"Invalid transformed matrix shape: {X_trans.shape}, expected (1, 7).")
    if np.isnan(X_trans).any() or np.isinf(X_trans).any():
        raise InferenceExecutionError("Transformed feature matrix contains NaN or Inf.")

    # 4. GAM Inference using predict_mu (exact Phase-5 method)
    try:
        raw_prob = gam_model.predict_mu(X_trans)[0]
    except Exception as e:
        raise InferenceExecutionError(f"GAM model prediction error: {str(e)}") from e

    # Validate output probability
    prob_float = float(raw_prob)
    if not np.isfinite(prob_float) or np.isnan(prob_float):
        raise InferenceExecutionError(f"GAM returned non-finite probability: {raw_prob}")
    if prob_float < 0.0 or prob_float > 1.0:
        raise InferenceExecutionError(f"GAM probability out of bounds [0, 1]: {prob_float}")

    # 5. Exact threshold classification (Full precision, no rounding prior to comparison)
    referral = bool(prob_float >= FROZEN_DECISION_THRESHOLD)

    # 6. Format user-facing representation strings
    formatted_prob = f"{prob_float * 100:.1f}%"
    formatted_rec = (
        "Refer for Stage-2 Confirmatory HbA1c Assessment"
        if referral
        else "Routine Care / Re-screen in 3 Years"
    )

    import datetime
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return ScreeningInferenceResult(
        probability=prob_float,
        referral_recommended=referral,
        threshold=FROZEN_DECISION_THRESHOLD,
        model_name="GAM",
        model_version="Phase-5 GAM (λ=10.0, Splines=10)",
        preprocessor_version="FrozenPreprocessor (Phase-5 StandardScaler)",
        execution_timestamp=now_str,
        formatted_probability=formatted_prob,
        formatted_recommendation=formatted_rec,
        raw_transformed_vector=X_trans[0].tolist(),
    )
