"""
SHAP Explainer — generates feature-level explanations for predictions.

Uses SHAP (SHapley Additive exPlanations) to show WHY the model
made a particular prediction. Each feature gets a contribution value:
- Positive = pushes toward diabetes
- Negative = pushes away from diabetes
"""
import numpy as np
import shap
import pandas as pd
from . import model_loader

# Cache background data PER scaler (different scalers expect different features)
_background_cache = {}
_explainers = {}


def _get_background_data(scaler, scaler_features, n_samples=100):
    """
    Load a small background dataset for SHAP.
    SHAP needs a reference dataset to compute feature contributions.
    Cached per scaler file to handle different feature sets.
    """
    cache_key = tuple(scaler_features)
    if cache_key in _background_cache:
        return _background_cache[cache_key]
    
    from pathlib import Path
    data_path = Path(__file__).resolve().parent.parent.parent / 'clean_dataset.csv'
    
    df = pd.read_csv(str(data_path))
    
    # Only select the columns the scaler expects
    X = df[list(scaler_features)]
    
    # Take a random sample and scale it
    sample = X.sample(n=min(n_samples, len(X)), random_state=42)
    background = scaler.transform(sample.values)
    
    _background_cache[cache_key] = background
    return background


def explain_prediction(model_name, features_dict):
    """
    Generate SHAP explanation for a single prediction.
    
    Parameters:
    - model_name: str, which model to explain
    - features_dict: dict with patient features
    
    Returns:
    - dict with:
        'shap_values': dict mapping feature_name -> contribution value
        'base_value': float, the model's average prediction
        'feature_values': dict mapping feature_name -> actual input value
    """
    model, scaler = model_loader.get_model_and_scaler(model_name)
    config = model_loader.MODEL_REGISTRY[model_name]
    
    # Get the feature names THIS scaler was trained on
    scaler_features = list(getattr(scaler, 'feature_names_in_', model_loader.FEATURE_NAMES))
    
    # Prepare the input with ONLY the features the scaler expects
    features_array = np.array([[features_dict[f] for f in scaler_features]])
    features_scaled = scaler.transform(features_array)
    
    # Get background data for this scaler's feature set
    background = _get_background_data(scaler, scaler_features)
    
    # Create or retrieve cached explainer
    if model_name not in _explainers:
        if config['type'] == 'keras':
            def predict_fn(x):
                return model.predict(x, verbose=0).flatten()
            
            _explainers[model_name] = shap.KernelExplainer(predict_fn, background)
        elif config['type'] == 'sklearn':
            if hasattr(model, 'predict_proba'):
                def predict_fn(x):
                    proba = model.predict_proba(x)
                    proba = np.array(proba)
                    if proba.ndim == 2:
                        # Standard sklearn: shape (n_samples, n_classes)
                        return proba[:, 1]
                    else:
                        # pygam/GAM: shape (n_samples,) — already positive class
                        return proba
            else:
                def predict_fn(x):
                    return model.predict(x)
            
            _explainers[model_name] = shap.KernelExplainer(predict_fn, background)
    
    explainer = _explainers[model_name]
    
    # Compute SHAP values for this single prediction
    shap_values = explainer.shap_values(features_scaled, nsamples=100)
    
    # Handle different SHAP output shapes
    if isinstance(shap_values, list):
        shap_values = shap_values[0]
    if len(shap_values.shape) > 1:
        shap_values = shap_values[0]
    
    # Build the result — map SHAP values to the scaler's feature names,
    # then fill in zeros for any features the scaler didn't use
    shap_dict = {}
    feature_values = {}
    
    for i, feature_name in enumerate(scaler_features):
        shap_dict[feature_name] = float(shap_values[i])
    
    # Include ALL features in the output (with 0.0 for features not in scaler)
    for feature_name in model_loader.FEATURE_NAMES:
        if feature_name not in shap_dict:
            shap_dict[feature_name] = 0.0
        feature_values[feature_name] = float(features_dict[feature_name])
    
    base_value = float(explainer.expected_value)
    if isinstance(base_value, np.ndarray):
        base_value = float(base_value[0])
    
    return {
        'shap_values': shap_dict,
        'base_value': base_value,
        'feature_values': feature_values,
    }


# Human-readable labels for feature values (for display in templates)
FEATURE_LABELS = {
    'gender': {0: 'Female', 1: 'Male', 2: 'Other'},
    'hypertension': {0: 'No', 1: 'Yes'},
    'heart_disease': {0: 'No', 1: 'Yes'},
    'smoking': {0: 'Never', 1: 'Former', 2: 'Current', 3: 'Not Current', 4: 'Ever', 5: 'No Info'},
}

FEATURE_DISPLAY_NAMES = {
    'gender': 'Gender',
    'age': 'Age',
    'hypertension': 'Hypertension',
    'heart_disease': 'Heart Disease',
    'smoking': 'Smoking History',
    'bmi': 'BMI',
    'HbA1c': 'HbA1c Level',
    'glucose': 'Blood Glucose',
}
