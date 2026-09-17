"""
Model Loader — loads and caches all trained ML models at startup.

This module handles:
1. Loading TensorFlow/Keras models (.h5 files)
2. Loading scikit-learn models (.pkl files)
3. Loading scalers for feature normalization
4. Providing a unified predict() interface
"""
import os
import numpy as np
import joblib
import tensorflow as tf
from pathlib import Path

# Suppress TensorFlow warnings for cleaner output
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

# Path to the models directory (relative to the Skripsi root)
MODELS_DIR = Path(__file__).resolve().parent.parent.parent / 'models'

# Feature names in the order expected by the models
FEATURE_NAMES = ['gender', 'age', 'hypertension', 'heart_disease', 'smoking', 'bmi', 'HbA1c', 'glucose']

# Human-readable model names mapped to their files
MODEL_REGISTRY = {
    'DLNN Baseline': {
        'model_file': 'dlnn_model_A.h5',
        'scaler_file': 'scaler_A.pkl',
        'type': 'keras'
    },
    'DLNN + Class Weights': {
        'model_file': 'dlnn_model_A_weighted.h5',
        'scaler_file': 'scaler_A.pkl',
        'type': 'keras'
    },
    'DLNN + SMOTE': {
        'model_file': 'dlnn_model_A_smote.h5',
        'scaler_file': 'scaler_recall_improvement.pkl',
        'type': 'keras'
    },
    'DLNN + Focal Loss': {
        'model_file': 'dlnn_model_A_focal.h5',
        'scaler_file': 'scaler_recall_improvement.pkl',
        'type': 'keras'
    },
    'DLNN + SMOTE + Focal Loss': {
        'model_file': 'dlnn_model_A_smote_focal.h5',
        'scaler_file': 'scaler_recall_improvement.pkl',
        'type': 'keras'
    },
    'GAM': {
        'model_file': 'gam_model.pkl',
        'scaler_file': 'scaler_A.pkl',
        'type': 'sklearn'
    },
}

# Cache for loaded models and scalers
_loaded_models = {}
_loaded_scalers = {}


def _load_model(model_name):
    """Load a model from disk and cache it."""
    if model_name in _loaded_models:
        return _loaded_models[model_name]
    
    config = MODEL_REGISTRY.get(model_name)
    if not config:
        raise ValueError(f"Unknown model: {model_name}. Available: {list(MODEL_REGISTRY.keys())}")
    
    model_path = MODELS_DIR / config['model_file']
    
    if not model_path.exists():
        raise FileNotFoundError(f"Model file not found: {model_path}")
    
    if config['type'] == 'keras':
        model = tf.keras.models.load_model(str(model_path), compile=False)
    elif config['type'] == 'sklearn':
        model = joblib.load(str(model_path))
    else:
        raise ValueError(f"Unknown model type: {config['type']}")
    
    _loaded_models[model_name] = model
    return model


def _load_scaler(model_name):
    """Load the scaler associated with a model."""
    if model_name in _loaded_scalers:
        return _loaded_scalers[model_name]
    
    config = MODEL_REGISTRY.get(model_name)
    if not config:
        raise ValueError(f"Unknown model: {model_name}")
    
    scaler_path = MODELS_DIR / config['scaler_file']
    
    if not scaler_path.exists():
        raise FileNotFoundError(f"Scaler file not found: {scaler_path}")
    
    scaler = joblib.load(str(scaler_path))
    _loaded_scalers[model_name] = scaler
    return scaler


def predict(model_name, features_dict, threshold=0.5):
    """
    Make a prediction using the specified model.
    
    Parameters:
    - model_name: str, key from MODEL_REGISTRY
    - features_dict: dict with keys matching FEATURE_NAMES
    - threshold: float, classification threshold (default 0.5)
    
    Returns:
    - dict with 'prediction' (0/1), 'confidence' (float), 'probability' (float)
    """
    model = _load_model(model_name)
    scaler = _load_scaler(model_name)
    config = MODEL_REGISTRY[model_name]
    
    # Get the feature names the scaler was trained on
    scaler_features = list(getattr(scaler, 'feature_names_in_', FEATURE_NAMES))
    
    # Build array with ONLY the features the scaler expects, in the right order
    features_for_scaler = np.array([[features_dict[f] for f in scaler_features]])
    
    # Scale features
    features_scaled = scaler.transform(features_for_scaler)
    
    # Get prediction probability
    if config['type'] == 'keras':
        probability = float(model.predict(features_scaled, verbose=0).flatten()[0])
    elif config['type'] == 'sklearn':
        # For sklearn/pygam models with predict_proba
        if hasattr(model, 'predict_proba'):
            proba_result = model.predict_proba(features_scaled)
            proba_result = np.array(proba_result)
            
            if proba_result.ndim == 2:
                # Standard sklearn: shape (n_samples, n_classes) → take class 1
                probability = float(proba_result[0][1])
            else:
                # pygam/GAM: shape (n_samples,) → already the positive class prob
                probability = float(proba_result[0])
        else:
            probability = float(model.predict(features_scaled)[0])
    
    # Apply threshold
    prediction = 1 if probability >= threshold else 0
    
    return {
        'prediction': prediction,
        'confidence': probability if prediction == 1 else 1 - probability,
        'probability': probability,
    }


def get_available_models():
    """Return list of available model names."""
    available = []
    for name, config in MODEL_REGISTRY.items():
        model_path = MODELS_DIR / config['model_file']
        if model_path.exists():
            available.append(name)
    return available


def get_model_and_scaler(model_name):
    """Return the loaded model and scaler (for use by SHAP explainer)."""
    model = _load_model(model_name)
    scaler = _load_scaler(model_name)
    return model, scaler
