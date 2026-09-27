"""
NLP Feedback Interpreter for Human Feedback Learning Loop.

Interprets optional human free-text feedback by mapping it to the master
feedback taxonomy using TF-IDF vectorization + Logistic Regression.

DESIGN PRINCIPLES:
1. NLP is NOT the predictive model. It interprets optional free-text feedback.
2. The human-selected structured category is the CANONICAL learning signal.
3. NLP output is supplementary: it may confirm, refine, or flag discrepancies.
4. Raw human text is ALWAYS preserved for auditability.
5. NLP interpretation is ALWAYS preserved alongside raw text.
6. If NLP confidence < threshold, output maps to 'unmapped' (no learning signal).
7. NLP NEVER directly modifies model weights or parameters.

ARCHITECTURE:
    Human text → TF-IDF Vectorizer → Logistic Regression → Category scores
                                                          → Detected category
                                                          → Feature extraction
                                                          → Confidence score
"""

import re
import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

from .feedback_taxonomy import (
    FEEDBACK_CATEGORIES,
    FeedbackCategory,
    get_category,
    STAGE1_FEATURES,
    DIR_NO_LEARNING,
)

logger = logging.getLogger(__name__)

# Minimum confidence to accept NLP classification (below → 'unmapped')
DEFAULT_NLP_CONFIDENCE_THRESHOLD: float = 0.50


@dataclass(frozen=True)
class FeedbackNLPResult:
    """Immutable container for NLP interpretation of free-text feedback."""
    detected_category: str              # Master taxonomy category_id
    relevant_feature: Optional[str]     # One of 7 Stage-1 predictors or None
    direction: str                      # Learning direction from taxonomy
    confidence: float                   # Classification confidence [0, 1]
    raw_scores: Dict[str, float]        # Per-category classification scores
    method: str = "tfidf_logistic_v1"   # NLP method identifier
    is_above_threshold: bool = True     # Whether confidence >= threshold

    def to_dict(self) -> dict:
        return {
            "detected_category": self.detected_category,
            "relevant_feature": self.relevant_feature,
            "direction": self.direction,
            "confidence": round(self.confidence, 4),
            "raw_scores": {k: round(v, 4) for k, v in self.raw_scores.items()},
            "method": self.method,
            "is_above_threshold": self.is_above_threshold,
        }


# ---------------------------------------------------------------------------
# Seed Training Corpus
# ---------------------------------------------------------------------------
# Each entry: (text, category_id)
# This curated seed corpus trains the NLP classifier to map free-text phrases
# to master taxonomy categories. ~10-15 examples per category.

SEED_CORPUS: List[Tuple[str, str]] = [
    # bmi_overweighted
    ("BMI is being weighted too strongly", "bmi_overweighted"),
    ("the BMI is high but the person is physically active", "bmi_overweighted"),
    ("BMI has too much influence on the result", "bmi_overweighted"),
    ("body mass index is overemphasized", "bmi_overweighted"),
    ("the model relies too heavily on BMI", "bmi_overweighted"),
    ("BMI alone should not drive this referral", "bmi_overweighted"),
    ("high BMI but muscular build", "bmi_overweighted"),
    ("BMI overweighted in this assessment", "bmi_overweighted"),
    ("too much weight on body mass index", "bmi_overweighted"),
    ("BMI is misleading for athletic patients", "bmi_overweighted"),

    # bmi_underweighted
    ("BMI should matter more in this case", "bmi_underweighted"),
    ("the BMI contribution seems too low", "bmi_underweighted"),
    ("body mass index should have more influence", "bmi_underweighted"),
    ("BMI is an important risk factor here", "bmi_underweighted"),
    ("the model underestimates the BMI effect", "bmi_underweighted"),
    ("BMI should weigh more heavily", "bmi_underweighted"),
    ("low influence of BMI is concerning", "bmi_underweighted"),
    ("need more emphasis on body mass", "bmi_underweighted"),
    ("BMI underweighted for this patient profile", "bmi_underweighted"),
    ("body mass index matters more than shown", "bmi_underweighted"),

    # age_overweighted
    ("age is being weighted too strongly", "age_overweighted"),
    ("age has too much influence", "age_overweighted"),
    ("the patient is young but the age factor is too dominant", "age_overweighted"),
    ("age overweighted in the screening", "age_overweighted"),
    ("too much emphasis on age alone", "age_overweighted"),
    ("age should not dominate the prediction", "age_overweighted"),
    ("the model puts too much weight on age", "age_overweighted"),
    ("despite the age the other factors suggest otherwise", "age_overweighted"),
    ("age contribution is excessive", "age_overweighted"),
    ("elderly age is overemphasized here", "age_overweighted"),

    # age_underweighted
    ("age should matter more here", "age_underweighted"),
    ("the age factor is too low", "age_underweighted"),
    ("age is an important risk factor being underweighted", "age_underweighted"),
    ("the model underestimates the age effect", "age_underweighted"),
    ("need more emphasis on patient age", "age_underweighted"),
    ("age contribution seems insufficient", "age_underweighted"),
    ("older age should increase the risk more", "age_underweighted"),
    ("age is underweighted in this assessment", "age_underweighted"),
    ("the patient age warrants more concern", "age_underweighted"),
    ("age should have more influence on the result", "age_underweighted"),

    # waist_overweighted
    ("waist circumference is overweighted", "waist_overweighted"),
    ("waist measurement has too much influence", "waist_overweighted"),
    ("the waist contribution is too high", "waist_overweighted"),
    ("too much weight on waist size", "waist_overweighted"),
    ("waist circumference overemphasized", "waist_overweighted"),
    ("waist is not the most relevant factor here", "waist_overweighted"),
    ("the model relies too much on waist measurement", "waist_overweighted"),
    ("waist circumference should matter less", "waist_overweighted"),

    # waist_underweighted
    ("waist circumference should matter more", "waist_underweighted"),
    ("waist measurement is underweighted", "waist_underweighted"),
    ("the waist contribution seems too low", "waist_underweighted"),
    ("central obesity is not being captured enough", "waist_underweighted"),
    ("need more emphasis on waist circumference", "waist_underweighted"),
    ("the abdominal measurement is important here", "waist_underweighted"),
    ("waist size is a key risk factor", "waist_underweighted"),
    ("more weight should be on waist circumference", "waist_underweighted"),

    # sedentary_overweighted
    ("sedentary time is overweighted", "sedentary_overweighted"),
    ("sitting time has too much influence", "sedentary_overweighted"),
    ("sedentary minutes are overemphasized", "sedentary_overweighted"),
    ("the model weights sedentary behavior too heavily", "sedentary_overweighted"),
    ("physical inactivity contribution is too high", "sedentary_overweighted"),
    ("sedentary time should matter less", "sedentary_overweighted"),
    ("too much emphasis on daily sitting time", "sedentary_overweighted"),
    ("the sedentary factor is excessive", "sedentary_overweighted"),

    # sedentary_underweighted
    ("sedentary time should matter more", "sedentary_underweighted"),
    ("physical inactivity is underweighted", "sedentary_underweighted"),
    ("sedentary behavior is a key risk factor", "sedentary_underweighted"),
    ("the model underestimates sedentary time effect", "sedentary_underweighted"),
    ("more emphasis needed on sitting time", "sedentary_underweighted"),
    ("sedentary minutes should have more influence", "sedentary_underweighted"),
    ("daily inactivity is important here", "sedentary_underweighted"),
    ("the sedentary contribution is too low", "sedentary_underweighted"),

    # hypertension_context
    ("the patient has managed hypertension under control", "hypertension_context"),
    ("hypertension context is more nuanced", "hypertension_context"),
    ("the hypertension history needs clinical context", "hypertension_context"),
    ("blood pressure is well controlled with medication", "hypertension_context"),
    ("hypertension status does not tell the full story", "hypertension_context"),
    ("the hypertension situation is different than indicated", "hypertension_context"),
    ("additional context about blood pressure history", "hypertension_context"),
    ("hypertension is not a concern in this specific case", "hypertension_context"),

    # smoking_context
    ("the patient quit smoking years ago", "smoking_context"),
    ("smoking history is more nuanced", "smoking_context"),
    ("the smoking context differs from what the model assumes", "smoking_context"),
    ("the patient only smoked briefly", "smoking_context"),
    ("smoking cessation was long ago", "smoking_context"),
    ("the smoking history needs clinical context", "smoking_context"),
    ("former smoker with low pack-years", "smoking_context"),
    ("smoking status is not straightforward", "smoking_context"),

    # sex_context
    ("sex-related clinical factors are relevant", "sex_context"),
    ("the patient has sex-specific risk factors", "sex_context"),
    ("gender-related clinical context matters here", "sex_context"),
    ("hormonal factors affect the risk differently", "sex_context"),
    ("sex-specific considerations are important", "sex_context"),
    ("the sex factor needs clinical nuance", "sex_context"),
    ("male/female specific risk profile", "sex_context"),
    ("biological sex context differs", "sex_context"),

    # general_risk_too_high
    ("the overall risk seems too high", "general_risk_too_high"),
    ("the screening probability is overestimated", "general_risk_too_high"),
    ("the model is too aggressive in flagging this case", "general_risk_too_high"),
    ("this patient does not need referral", "general_risk_too_high"),
    ("the risk assessment is inflated", "general_risk_too_high"),
    ("overall the probability seems too elevated", "general_risk_too_high"),
    ("the screening signal is too high for this profile", "general_risk_too_high"),
    ("the model overestimates the risk here", "general_risk_too_high"),
    ("probability too high for this case", "general_risk_too_high"),
    ("the referral recommendation is too cautious", "general_risk_too_high"),

    # general_risk_too_low
    ("the overall risk seems too low", "general_risk_too_low"),
    ("the screening probability is underestimated", "general_risk_too_low"),
    ("the model is missing risk factors", "general_risk_too_low"),
    ("this patient should be referred", "general_risk_too_low"),
    ("the risk assessment is too conservative", "general_risk_too_low"),
    ("overall the probability seems too low", "general_risk_too_low"),
    ("the screening signal should be higher", "general_risk_too_low"),
    ("the model underestimates the risk here", "general_risk_too_low"),
    ("probability too low for this case", "general_risk_too_low"),
    ("the patient has concerning signs not captured", "general_risk_too_low"),

    # unmapped
    ("I disagree with the result", "unmapped"),
    ("not sure why", "unmapped"),
    ("just a feeling", "unmapped"),
    ("no specific reason", "unmapped"),
    ("I have my reasons", "unmapped"),
    ("other clinical judgment", "unmapped"),
    ("general disagreement", "unmapped"),
    ("test feedback", "unmapped"),
]


# ---------------------------------------------------------------------------
# Feature keyword extraction (supplementary to NLP classification)
# ---------------------------------------------------------------------------
FEATURE_KEYWORDS: Dict[str, List[str]] = {
    "bmi": ["bmi", "body mass", "body mass index", "weight", "obesity", "obese", "overweight", "muscular"],
    "age": ["age", "old", "young", "elderly", "years old", "aging"],
    "waist_cm": ["waist", "waist circumference", "abdominal", "belly", "central obesity"],
    "sedentary_minutes_day": ["sedentary", "sitting", "inactive", "inactivity", "physical activity", "exercise", "active"],
    "hypertension_history": ["hypertension", "blood pressure", "high blood pressure", "bp"],
    "smoking_history": ["smoking", "smoker", "cigarette", "tobacco", "quit smoking", "pack-years"],
    "sex": ["sex", "gender", "male", "female", "hormonal", "men", "women"],
}


def _extract_relevant_feature(text: str) -> Optional[str]:
    """Extract the most likely relevant feature from text using keyword matching."""
    text_lower = text.lower()
    feature_scores: Dict[str, int] = {}
    for feature, keywords in FEATURE_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in text_lower)
        if score > 0:
            feature_scores[feature] = score
    if not feature_scores:
        return None
    return max(feature_scores, key=feature_scores.get)


# ---------------------------------------------------------------------------
# NLP Pipeline
# ---------------------------------------------------------------------------

class FeedbackNLPInterpreter:
    """
    TF-IDF + Logistic Regression classifier for mapping free-text
    feedback to master taxonomy categories.

    Thread-safe after initialization (sklearn Pipeline is read-only after fit).
    """

    def __init__(self, confidence_threshold: float = DEFAULT_NLP_CONFIDENCE_THRESHOLD):
        self.confidence_threshold = confidence_threshold
        self._pipeline: Optional[Pipeline] = None
        self._categories: List[str] = []
        self._is_fitted = False

    def fit(self, corpus: Optional[List[Tuple[str, str]]] = None) -> "FeedbackNLPInterpreter":
        """
        Train the NLP pipeline on the seed corpus.
        If no corpus is provided, uses the built-in SEED_CORPUS.
        """
        if corpus is None:
            corpus = SEED_CORPUS

        if len(corpus) < 10:
            raise ValueError(f"Corpus too small ({len(corpus)} entries). Need at least 10.")

        texts = [t for t, _ in corpus]
        labels = [l for _, l in corpus]

        # Validate all labels exist in taxonomy
        for label in set(labels):
            if label not in FEEDBACK_CATEGORIES:
                raise ValueError(f"Corpus label '{label}' not found in feedback taxonomy.")

        self._categories = sorted(set(labels))

        self._pipeline = Pipeline([
            ("tfidf", TfidfVectorizer(
                max_features=500,
                ngram_range=(1, 2),
                stop_words="english",
                lowercase=True,
                min_df=1,
            )),
            ("clf", LogisticRegression(
                max_iter=1000,
                solver="lbfgs",
                C=1.0,
                random_state=42,
            )),
        ])

        self._pipeline.fit(texts, labels)
        self._is_fitted = True
        logger.info(
            f"FeedbackNLPInterpreter fitted on {len(texts)} examples, "
            f"{len(self._categories)} categories."
        )
        return self

    def interpret(self, text: str) -> FeedbackNLPResult:
        """
        Interpret a free-text feedback string and map it to the master taxonomy.

        Returns FeedbackNLPResult with detected category, confidence, and scores.
        If confidence < threshold, detected_category defaults to 'unmapped'.
        """
        if not self._is_fitted or self._pipeline is None:
            raise RuntimeError("FeedbackNLPInterpreter has not been fitted. Call fit() first.")

        if not text or not text.strip():
            return FeedbackNLPResult(
                detected_category="unmapped",
                relevant_feature=None,
                direction=DIR_NO_LEARNING,
                confidence=0.0,
                raw_scores={},
                is_above_threshold=False,
            )

        cleaned_text = text.strip()

        # Predict probabilities for all categories
        proba = self._pipeline.predict_proba([cleaned_text])[0]
        classes = self._pipeline.classes_

        raw_scores = {cls: float(prob) for cls, prob in zip(classes, proba)}

        # Find best category
        best_idx = int(np.argmax(proba))
        best_category_id = classes[best_idx]
        best_confidence = float(proba[best_idx])

        # Confidence threshold gate
        if best_confidence < self.confidence_threshold:
            best_category_id = "unmapped"
            is_above = False
        else:
            is_above = True

        # Look up taxonomy metadata
        category = get_category(best_category_id)
        if category is None:
            best_category_id = "unmapped"
            category = get_category("unmapped")
            is_above = False

        # Extract relevant feature (from taxonomy first, keyword fallback)
        relevant_feature = None
        if category and category.relevant_features:
            relevant_feature = category.relevant_features[0]
        else:
            relevant_feature = _extract_relevant_feature(cleaned_text)

        direction = category.learning_direction if category else DIR_NO_LEARNING

        return FeedbackNLPResult(
            detected_category=best_category_id,
            relevant_feature=relevant_feature,
            direction=direction,
            confidence=best_confidence,
            raw_scores=raw_scores,
            method="tfidf_logistic_v1",
            is_above_threshold=is_above,
        )

    @property
    def is_fitted(self) -> bool:
        return self._is_fitted


# ---------------------------------------------------------------------------
# Singleton / module-level convenience
# ---------------------------------------------------------------------------
_INTERPRETER_INSTANCE: Optional[FeedbackNLPInterpreter] = None


def get_nlp_interpreter() -> FeedbackNLPInterpreter:
    """Return a fitted singleton NLP interpreter."""
    global _INTERPRETER_INSTANCE
    if _INTERPRETER_INSTANCE is None or not _INTERPRETER_INSTANCE.is_fitted:
        _INTERPRETER_INSTANCE = FeedbackNLPInterpreter()
        _INTERPRETER_INSTANCE.fit()
    return _INTERPRETER_INSTANCE


def interpret_feedback_text(text: str) -> FeedbackNLPResult:
    """Convenience function: interpret feedback text using the singleton interpreter."""
    return get_nlp_interpreter().interpret(text)
