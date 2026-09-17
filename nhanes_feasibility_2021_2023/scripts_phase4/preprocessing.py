#!/usr/bin/env python3
"""
Phase 4 — Script 2/7: Preprocessing Pipeline & Leakage Guard
Provides:
- Strict assertion guarding against prohibited variables entering X
- Isolated StandardScaler fitting on training folds only
- Explicit, documented binary categorical mapping
"""
from typing import List, Tuple
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler

PROHIBITED_LEAKAGE_VARS = {
    "SEQN", "LBXGH", "LBXGLU",
    "hba1c_category", "hba1c_dysglycemia",
    "fpg_category", "fpg_dysglycemia",
    "DIQ010", "DIQ160", "DIQ180",
    "WTINT2YR", "WTMEC2YR", "WTPH2YR", "WTSAF2YR",
    "SDMVSTRA", "SDMVPSU",
}

CORE_FEATURES = ["age", "sex", "bmi", "hypertension_history", "smoking_history"]
EXPANDED_FEATURES = CORE_FEATURES + ["waist_cm", "sedentary_minutes_day"]

CONTINUOUS_CORE = ["age", "bmi"]
CONTINUOUS_EXPANDED = ["age", "bmi", "waist_cm", "sedentary_minutes_day"]
CATEGORICAL_FEATURES = ["sex", "hypertension_history", "smoking_history"]


def assert_no_leakage(feature_list: List[str]):
    """Strictly assert that no prohibited variable ever enters feature set."""
    intersection = set(feature_list) & PROHIBITED_LEAKAGE_VARS
    if intersection:
        raise ValueError(
            f"CRITICAL DATA LEAKAGE VIOLATION! Prohibited variables detected in feature set: {intersection}"
        )


def encode_categoricals(df: pd.DataFrame) -> pd.DataFrame:
    """
    Explicit, documented categorical encoding:
    - sex: RIAGENDR (1=Male, 2=Female) -> 1=Male, 0=Female (binary indicator)
    - hypertension_history: BPQ020 (1=Yes, 2=No) -> 1=Yes, 0=No
    - smoking_history: SMQ020 (1=Yes, 2=No) -> 1=Yes, 0=No
    """
    out = df.copy()
    if "sex" in out.columns:
        out["sex"] = out["sex"].map({1.0: 1.0, 2.0: 0.0})
    if "hypertension_history" in out.columns:
        out["hypertension_history"] = out["hypertension_history"].map({1.0: 1.0, 2.0: 0.0})
    if "smoking_history" in out.columns:
        out["smoking_history"] = out["smoking_history"].map({1.0: 1.0, 2.0: 0.0})
    return out


class Preprocessor:
    """
    Fold-isolated preprocessor.
    Fits continuous scaler ONLY on training fold.
    """
    def __init__(self, feature_set: str = "core"):
        self.feature_set = feature_set
        if feature_set == "core":
            self.features = CORE_FEATURES.copy()
            self.continuous_cols = CONTINUOUS_CORE.copy()
        elif feature_set == "expanded":
            self.features = EXPANDED_FEATURES.copy()
            self.continuous_cols = CONTINUOUS_EXPANDED.copy()
        else:
            raise ValueError(f"Unknown feature_set: {feature_set}")

        assert_no_leakage(self.features)
        self.scaler = StandardScaler()
        self.is_fitted = False

    def fit_transform(self, df_train: pd.DataFrame) -> Tuple[np.ndarray, List[str]]:
        assert_no_leakage(self.features)
        df_encoded = encode_categoricals(df_train[self.features])

        # Scale continuous features on training fold only
        scaled_cont = self.scaler.fit_transform(df_encoded[self.continuous_cols])
        self.is_fitted = True

        # Combine continuous + categorical
        X_out = df_encoded.copy()
        X_out[self.continuous_cols] = scaled_cont
        return X_out.values.astype(np.float32), self.features

    def transform(self, df_val: pd.DataFrame) -> np.ndarray:
        if not self.is_fitted:
            raise RuntimeError("Preprocessor must be fit on training fold before transform!")
        assert_no_leakage(self.features)
        df_encoded = encode_categoricals(df_val[self.features])

        scaled_cont = self.scaler.transform(df_encoded[self.continuous_cols])
        X_out = df_encoded.copy()
        X_out[self.continuous_cols] = scaled_cont
        return X_out.values.astype(np.float32)
