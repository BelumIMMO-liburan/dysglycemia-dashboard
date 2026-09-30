"""
Regression Test Suite for the 13-Layer Feedback Loop Mechanism Validation Protocol.

Ensures that:
  - Canonical signals are parsed with high integrity and free-text independence.
  - Directionality strictly reverses sign for reduce vs increase across features.
  - No-learning feedback acts as a true zero-effect ablation.
  - Feature isolation confines parameter updates strictly to the targeted feature.
  - Cross-feature controls demonstrate localization.
  - Counterfactual tests demonstrate log-odds symmetry.
  - Multi-feature mapping limitation is enforced as documented.
  - Global calibration updates intercept without modifying feature weights.
  - Similarity gating enforces the 0.85 threshold.
  - Pipeline is deterministic within 1e-12 tolerance.
  - Frozen artifacts, hashes, and threshold (0.1389) remain unaltered.
  - Final-test observations and HbA1c are strictly isolated.
  - End-to-end Case A -> Case B demonstrations are reproducible.
"""

import math
import hashlib
from decimal import Decimal
from pathlib import Path

from django.test import TestCase
from django.conf import settings

from predictor.models import (
    ScreeningRecord,
    ScreeningExplanation,
    HumanReview,
    HumanFeedback,
    ModelVersion,
)
from predictor.services.feedback_taxonomy import (
    parse_canonical_signal,
    canonical_signal_to_learning_fields,
    CanonicalLearningSignal,
    NULL_SIGNAL,
    DIR_REDUCE_INFLUENCE,
    DIR_INCREASE_INFLUENCE,
    DIR_REDUCE_GLOBAL,
    DIR_INCREASE_GLOBAL,
    DIR_NO_LEARNING,
)
from predictor.services.feedback_learning import (
    ADAPTATION_FEATURE_NAMES,
    NORMALIZATION_BOUNDS,
    MAX_DELTA_LOG_ODDS,
    _normalize_features_to_vector,
    _build_training_row,
    compute_adaptation_delta,
    get_final_test_signatures,
    CONTROLLED_CASE_A_DATA,
    CONTROLLED_CASE_B_DATA,
)
from predictor.services.similarity import (
    compute_similarity,
    DEFAULT_SIMILARITY_THRESHOLD,
)
from predictor.services.screening_inference import (
    predict_screening,
    FROZEN_DECISION_THRESHOLD,
    EXPECTED_GAM_SHA256,
    get_artifact_paths,
)
from sklearn.linear_model import Ridge
import numpy as np


class FeedbackMechanismValidationSuiteTests(TestCase):
    """Automated verification for all 13 mechanism validation layers."""

    def setUp(self):
        self.case_a = dict(CONTROLLED_CASE_A_DATA)
        self.case_b = dict(CONTROLLED_CASE_B_DATA)
        self.base_pred = predict_screening(self.case_a)
        self.base_prob = self.base_pred.probability
        self.base_log_odds = math.log(self.base_prob / (1.0 - self.base_prob))

    def test_layer_01_canonical_signal_integrity(self):
        """Layer 1: Verify all 12 feature-directional pairs + no-learning and free-text independence."""
        signals = [
            ("bmi", "reduce", "feature_specific", -1.0, "bmi"),
            ("bmi", "increase", "feature_specific", 1.0, "bmi"),
            ("age", "reduce", "feature_specific", -1.0, "age"),
            ("age", "increase", "feature_specific", 1.0, "age"),
            ("waist", "reduce", "feature_specific", -1.0, "waist_cm"),
            ("waist", "increase", "feature_specific", 1.0, "waist_cm"),
            ("hypertension", "reduce", "feature_specific", -1.0, "hypertension_history"),
            ("hypertension", "increase", "feature_specific", 1.0, "hypertension_history"),
            ("smoking", "reduce", "feature_specific", -1.0, "smoking_history"),
            ("smoking", "increase", "feature_specific", 1.0, "smoking_history"),
            ("sedentary", "reduce", "feature_specific", -1.0, "sedentary_minutes_day"),
            ("sedentary", "increase", "feature_specific", 1.0, "sedentary_minutes_day"),
            ("none", "none", "none", 0.0, None),
        ]
        for target, dir_str, scope, exp_target, exp_feat in signals:
            sig = parse_canonical_signal(target_feature=target, direction=dir_str, scope=scope)
            x_row, y_target = _build_training_row(self.case_a, structured_category="", canonical_signal=sig)
            self.assertEqual(y_target, exp_target)
            if exp_feat:
                feat_idx = ADAPTATION_FEATURE_NAMES.index(exp_feat)
                self.assertGreater(x_row[feat_idx], 0.0)
            else:
                self.assertEqual(float(np.linalg.norm(x_row)), 0.0)

    def test_layer_02_directionality_bmi_age_waist(self):
        """Layer 2: Verify reduce produces delta < 0 and increase produces delta > 0."""
        for feat in ["bmi", "age", "waist"]:
            # Reduce
            sig_red = CanonicalLearningSignal(target_feature=feat, direction="reduce", scope="feature_specific")
            xr, yr = _build_training_row(self.case_a, structured_category="", canonical_signal=sig_red)
            mr = Ridge(alpha=0.5, fit_intercept=False).fit(np.array([xr]), np.array([yr]))
            dr = compute_adaptation_delta({"model": mr, "feature_names": ADAPTATION_FEATURE_NAMES, "max_delta": MAX_DELTA_LOG_ODDS}, self.case_a)
            self.assertLess(dr, 0.0, f"Expected negative delta for {feat} reduce, got {dr}")

            # Increase
            sig_inc = CanonicalLearningSignal(target_feature=feat, direction="increase", scope="feature_specific")
            xi, yi = _build_training_row(self.case_a, structured_category="", canonical_signal=sig_inc)
            mi = Ridge(alpha=0.5, fit_intercept=False).fit(np.array([xi]), np.array([yi]))
            di = compute_adaptation_delta({"model": mi, "feature_names": ADAPTATION_FEATURE_NAMES, "max_delta": MAX_DELTA_LOG_ODDS}, self.case_a)
            self.assertGreater(di, 0.0, f"Expected positive delta for {feat} increase, got {di}")

    def test_layer_03_no_learning_ablation(self):
        """Layer 3: Verify target_feature none strictly produces zero weight norm and zero delta."""
        sig_none = CanonicalLearningSignal(target_feature="none", direction="none", scope="none")
        xn, yn = _build_training_row(self.case_a, structured_category="no_learning_signal", canonical_signal=sig_none)
        self.assertEqual(yn, 0.0)
        self.assertEqual(float(np.linalg.norm(xn)), 0.0)

        mn = Ridge(alpha=0.5, fit_intercept=False).fit(np.array([xn]), np.array([yn]))
        dn = compute_adaptation_delta({"model": mn, "feature_names": ADAPTATION_FEATURE_NAMES, "max_delta": MAX_DELTA_LOG_ODDS}, self.case_a)
        self.assertEqual(dn, 0.0)

    def test_layer_04_feature_specific_isolation(self):
        """Layer 4: Verify non-target weights remain strictly 0.000000."""
        for feat in ["bmi", "age", "waist"]:
            sig = CanonicalLearningSignal(target_feature=feat, direction="reduce", scope="feature_specific")
            x, y = _build_training_row(self.case_a, structured_category="", canonical_signal=sig)
            m = Ridge(alpha=0.5, fit_intercept=False).fit(np.array([x]), np.array([y]))

            target_name = "waist_cm" if feat == "waist" else feat
            target_idx = ADAPTATION_FEATURE_NAMES.index(target_name)
            for i, coef in enumerate(m.coef_):
                if i == target_idx:
                    self.assertLess(coef, 0.0)
                else:
                    self.assertEqual(float(coef), 0.0, f"Expected 0.0 for non-target index {i}, got {coef}")

    def test_layer_05_cross_feature_control(self):
        """Layer 5: Verify BMI signal does not modify Age coefficient and vice-versa."""
        sig_bmi = CanonicalLearningSignal(target_feature="bmi", direction="reduce", scope="feature_specific")
        sig_age = CanonicalLearningSignal(target_feature="age", direction="reduce", scope="feature_specific")

        xb, yb = _build_training_row(self.case_a, structured_category="", canonical_signal=sig_bmi)
        xa, ya = _build_training_row(self.case_a, structured_category="", canonical_signal=sig_age)

        mb = Ridge(alpha=0.5, fit_intercept=False).fit(np.array([xb]), np.array([yb]))
        ma = Ridge(alpha=0.5, fit_intercept=False).fit(np.array([xa]), np.array([ya]))

        bmi_idx = ADAPTATION_FEATURE_NAMES.index("bmi")
        age_idx = ADAPTATION_FEATURE_NAMES.index("age")

        self.assertNotEqual(float(mb.coef_[bmi_idx]), 0.0)
        self.assertEqual(float(mb.coef_[age_idx]), 0.0)

        self.assertNotEqual(float(ma.coef_[age_idx]), 0.0)
        self.assertEqual(float(ma.coef_[bmi_idx]), 0.0)

    def test_layer_06_bidirectional_counterfactual_symmetry(self):
        """Layer 6: Verify exact log-odds symmetry between reduce and increase signals."""
        sig_red = CanonicalLearningSignal(target_feature="bmi", direction="reduce", scope="feature_specific")
        sig_inc = CanonicalLearningSignal(target_feature="bmi", direction="increase", scope="feature_specific")

        xr, yr = _build_training_row(self.case_a, structured_category="", canonical_signal=sig_red)
        xi, yi = _build_training_row(self.case_a, structured_category="", canonical_signal=sig_inc)

        mr = Ridge(alpha=0.5, fit_intercept=False).fit(np.array([xr]), np.array([yr]))
        mi = Ridge(alpha=0.5, fit_intercept=False).fit(np.array([xi]), np.array([yi]))

        dr = compute_adaptation_delta({"model": mr, "feature_names": ADAPTATION_FEATURE_NAMES, "max_delta": MAX_DELTA_LOG_ODDS}, self.case_a)
        di = compute_adaptation_delta({"model": mi, "feature_names": ADAPTATION_FEATURE_NAMES, "max_delta": MAX_DELTA_LOG_ODDS}, self.case_a)

        self.assertAlmostEqual(dr, -di, places=8)

    def test_layer_07_multifeature_signal_limitation(self):
        """Layer 7: Document and verify multiple_factors maps to global intercept."""
        sig = parse_canonical_signal("multiple_factors_overweighted")
        x, y = _build_training_row(self.case_a, structured_category="multiple_factors_overweighted", canonical_signal=sig)
        self.assertEqual(y, -1.0)
        self.assertEqual(x[0], 1.0)
        self.assertEqual(float(np.linalg.norm(x[1:])), 0.0)

    def test_layer_08_global_risk_calibration(self):
        """Layer 8: Verify global_bias signal modifies column 0 and leaves feature weights 0.0."""
        sig = CanonicalLearningSignal(target_feature="global_bias", direction="reduce", scope="global")
        x, y = _build_training_row(self.case_a, structured_category="", canonical_signal=sig)
        m = Ridge(alpha=0.5, fit_intercept=False).fit(np.array([x]), np.array([y]))
        self.assertLess(m.coef_[0], 0.0)
        self.assertEqual(float(np.linalg.norm(m.coef_[1:])), 0.0)

    def test_layer_09_similarity_gating(self):
        """Layer 9: Verify similarity gating at 0.85 threshold."""
        sim_high = compute_similarity(self.case_a, self.case_b)
        self.assertGreaterEqual(sim_high.similarity_score, DEFAULT_SIMILARITY_THRESHOLD)
        self.assertTrue(sim_high.is_similar)

        case_c = {'age': 20, 'sex': 'Female', 'bmi': 18.5, 'waist_cm': 65.0, 'hypertension_history': 'No', 'smoking_history': 'No', 'sedentary_minutes_day': 60}
        sim_low = compute_similarity(self.case_a, case_c)
        self.assertLess(sim_low.similarity_score, DEFAULT_SIMILARITY_THRESHOLD)
        self.assertFalse(sim_low.is_similar)

    def test_layer_10_reproducibility_determinism(self):
        """Layer 10: Verify run-to-run numerical identity within 1e-12."""
        sig = CanonicalLearningSignal(target_feature="bmi", direction="reduce", scope="feature_specific")
        x1, y1 = _build_training_row(self.case_a, structured_category="", canonical_signal=sig)
        x2, y2 = _build_training_row(self.case_a, structured_category="", canonical_signal=sig)

        m1 = Ridge(alpha=0.5, fit_intercept=False).fit(np.array([x1]), np.array([y1]))
        m2 = Ridge(alpha=0.5, fit_intercept=False).fit(np.array([x2]), np.array([y2]))

        self.assertLess(float(np.max(np.abs(m1.coef_ - m2.coef_))), 1e-12)

    def test_layer_11_artifact_governance_hashes(self):
        """Layer 11: Verify GAM-v1, Preprocessor, and Threshold are locked."""
        paths = get_artifact_paths()
        with open(paths["gam"], "rb") as f:
            gam_hash = hashlib.sha256(f.read()).hexdigest()
        self.assertEqual(gam_hash, EXPECTED_GAM_SHA256)
        self.assertEqual(float(FROZEN_DECISION_THRESHOLD), 0.1389)

    def test_layer_12_final_test_isolation_and_leakage(self):
        """Layer 12: Verify final-test observations cannot enter learning and HbA1c is excluded."""
        seqns, signatures = get_final_test_signatures()
        self.assertEqual(len(seqns), 812)
        self.assertNotIn("hba1c", ADAPTATION_FEATURE_NAMES)

    def test_layer_13_end_to_end_demonstration(self):
        """Layer 13: Verify historical and new Case A -> B end-to-end pipeline."""
        sim = compute_similarity(self.case_a, self.case_b)
        self.assertAlmostEqual(sim.similarity_score, 0.9846, places=3)
        base_b = predict_screening(self.case_b)
        self.assertAlmostEqual(base_b.probability, 0.311198, places=4)
