"""
Stage-1 Non-Laboratory Screening Input Schema
Authoritative UI/Domain Contract for Phase D2.2

Governing Specifications:
- FINAL_MODEL_SPECIFICATION_LOCKED.md (Section 3.2: 7 Frozen Non-Laboratory Predictors)
- research-governance skill (Strict research boundary; immutable features)
- dashboard-design skill (Clinical neutral UI tokens and clear human semantics)

CRITICAL GOVERNANCE NOTE:
This schema is a UI/domain contract only. It DOES NOT import or execute
the frozen GAM model or preprocessor. Model inference encoding belongs to Phase D2.3.
"""

from typing import Dict, Any, List, Tuple


# Canonical ordering of Stage-1 predictors matching the frozen research protocol
CANONICAL_PREDICTOR_ORDER: List[str] = [
    'age',
    'sex',
    'bmi',
    'hypertension_history',
    'smoking_history',
    'waist_cm',
    'sedentary_minutes_day',
]

# Supported categorical choices with human-readable values
SEX_CHOICES: Tuple[Tuple[str, str], ...] = (
    ('male', 'Male'),
    ('female', 'Female'),
)

HYPERTENSION_CHOICES: Tuple[Tuple[str, str], ...] = (
    ('yes', 'Yes'),
    ('no', 'No'),
)

SMOKING_CHOICES: Tuple[Tuple[str, str], ...] = (
    ('yes', 'Yes'),
    ('no', 'No'),
)

# Comprehensive field metadata dictionary
STAGE1_INPUT_SCHEMA: Dict[str, Dict[str, Any]] = {
    'age': {
        'canonical_name': 'age',
        'source_variable': 'RIDAGEYR',
        'label': 'Age',
        'section': 'demographic',
        'section_title': '1. Demographic Information',
        'data_type': 'integer',
        'unit': 'years',
        'required': True,
        'min_value': 18,
        'max_value': 80,
        'step': 1,
        'precision': 0,
        'description': 'Age in completed years. Valid model-supported research range: 18–80 years (80 represents top-coded values in NHANES).',
        'help_text': 'Valid model-supported research range: 18 to 80 years.',
        'placeholder': 'e.g., 52',
        'model_encoding_contract': 'Continuous feature transformed by StandardScaler during Phase D2.3.',
    },
    'sex': {
        'canonical_name': 'sex',
        'source_variable': 'RIAGENDR',
        'label': 'Sex',
        'section': 'demographic',
        'section_title': '1. Demographic Information',
        'data_type': 'categorical',
        'unit': None,
        'required': True,
        'choices': SEX_CHOICES,
        'description': 'Biological sex as recorded in the research protocol. The frozen GAM model supports binary categories: Male or Female.',
        'help_text': 'Biological sex as recorded in the research protocol.',
        'model_encoding_contract': 'Binary factor f(1): male -> 1, female -> 0.',
    },
    'bmi': {
        'canonical_name': 'bmi',
        'source_variable': 'BMXBMI',
        'label': 'Body Mass Index (BMI)',
        'section': 'body_measurements',
        'section_title': '2. Body Measurements',
        'data_type': 'float',
        'unit': 'kg/m²',
        'required': True,
        'min_value': 11.1,
        'max_value': 69.9,
        'step': 0.1,
        'precision': 1,
        'description': 'Body mass index in kg/m². Valid development-supported research range: 11.1–69.9 kg/m².',
        'help_text': 'Valid model-supported research range: 11.1 to 69.9 kg/m².',
        'placeholder': 'e.g., 28.4',
        'model_encoding_contract': 'Continuous feature transformed by StandardScaler during Phase D2.3.',
    },
    'waist_cm': {
        'canonical_name': 'waist_cm',
        'source_variable': 'BMXWAIST',
        'label': 'Waist Circumference',
        'section': 'body_measurements',
        'section_title': '2. Body Measurements',
        'data_type': 'float',
        'unit': 'cm',
        'required': True,
        'min_value': 60.0,
        'max_value': 187.0,
        'step': 0.1,
        'precision': 1,
        'description': 'Waist circumference in centimeters. Valid development-supported research range: 60.0–187.0 cm.',
        'help_text': 'Valid model-supported research range: 60.0 to 187.0 cm.',
        'placeholder': 'e.g., 98.5',
        'model_encoding_contract': 'Continuous feature transformed by StandardScaler during Phase D2.3.',
    },
    'hypertension_history': {
        'canonical_name': 'hypertension_history',
        'source_variable': 'BPQ020',
        'label': 'History of Hypertension',
        'section': 'health_history',
        'section_title': '3. Health History',
        'data_type': 'categorical',
        'unit': None,
        'required': True,
        'choices': HYPERTENSION_CHOICES,
        'description': 'Self-reported prior diagnosis: ever told by a doctor or health professional that you have hypertension / high blood pressure.',
        'help_text': 'Ever diagnosed with high blood pressure by a health professional.',
        'model_encoding_contract': 'Binary factor f(3): yes -> 1, no -> 0.',
    },
    'smoking_history': {
        'canonical_name': 'smoking_history',
        'source_variable': 'SMQ020',
        'label': 'Smoking History',
        'section': 'health_history',
        'section_title': '3. Health History',
        'data_type': 'categorical',
        'unit': None,
        'required': True,
        'choices': SMOKING_CHOICES,
        'description': 'Lifetime smoking history: smoked at least 100 cigarettes in entire lifetime (NHANES criteria).',
        'help_text': 'Smoked at least 100 cigarettes in lifetime (NHANES criteria).',
        'model_encoding_contract': 'Binary factor f(4): yes -> 1, no -> 0.',
    },
    'sedentary_minutes_day': {
        'canonical_name': 'sedentary_minutes_day',
        'source_variable': 'PAD680',
        'label': 'Sedentary Time',
        'section': 'daily_activity',
        'section_title': '4. Daily Activity',
        'data_type': 'integer',
        'unit': 'minutes/day',
        'required': True,
        'min_value': 0,
        'max_value': 1200,
        'step': 1,
        'precision': 0,
        'sentinel_codes': [7777, 9999],
        'description': 'Time spent sitting or reclining per typical day (excluding sleep). Valid research support: 0–1200 minutes/day (0 to 20 hours/day). Sentinel codes (7777, 9999) are strictly rejected.',
        'help_text': 'Time spent sitting or reclining on a typical day (0 to 1200 min/day).',
        'placeholder': 'e.g., 480',
        'model_encoding_contract': 'Continuous feature transformed by StandardScaler during Phase D2.3.',
    },
}


def get_field_schema(field_name: str) -> Dict[str, Any]:
    """Retrieve schema definition for a specific field name."""
    if field_name not in STAGE1_INPUT_SCHEMA:
        raise KeyError(f"Field '{field_name}' is not one of the 7 locked Stage-1 predictors.")
    return STAGE1_INPUT_SCHEMA[field_name]


def get_canonical_fields() -> List[Dict[str, Any]]:
    """Return all field definitions in canonical predictor order."""
    return [STAGE1_INPUT_SCHEMA[name] for name in CANONICAL_PREDICTOR_ORDER]
