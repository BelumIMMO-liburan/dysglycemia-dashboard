"""
Comprehensive Test Suite for Human Feedback Learning Loop.
Phase D2.9 & Research Governance Verification Suite

Covers:
1. FeedbackTaxonomyTests
2. FeedbackNLPTests
3. SimilarityServiceTests
4. ModelVersioningServiceTests
5. FeedbackLearningServiceTests
6. AdaptedInferenceTests
7. TechnicalValidationChecksTests (13 executable checks)
8. FinalTestLeakageProtectionTests
9. FeedbackDirectionSemanticsTests (6 learning directions)
10. CaseAToCaseBExperimentTests (Part 8 controlled experiment)
11. AuditTrailImmutabilityTests (Historical immutability)
"""

from decimal import Decimal
import hashlib
import json
from pathlib import Path
from django.test import TestCase, Client
from django.urls import reverse

from predictor.models import (
    ScreeningRecord,
    ScreeningExplanation,
    HumanReview,
    HumanFeedback,
    ModelVersion,
    FeedbackLearningBatch,
    SimilarCaseComparison,
)
from predictor.services.feedback_taxonomy import (
    get_category,
    get_active_categories,
    get_learnable_categories,
    validate_category_id,
    get_taxonomy_version,
    DIR_NO_LEARNING,
    DIR_REDUCE_INFLUENCE,
    DIR_INCREASE_INFLUENCE,
    DIR_REDUCE_GLOBAL,
    DIR_INCREASE_GLOBAL,
    DIR_CONTEXTUAL,
    STAGE1_FEATURES,
)
from predictor.services.feedback_nlp import (
    interpret_feedback_text,
    FeedbackNLPResult,
)
from predictor.services.similarity import (
    compute_similarity,
    DEFAULT_SIMILARITY_THRESHOLD,
    CANONICAL_PREDICTOR_ORDER,
)
from predictor.services.model_versioning import (
    get_active_version,
    get_baseline_version,
    rollback_to_version,
    validate_candidate,
    activate_version,
    create_candidate_version,
    BASELINE_VERSION_LABEL,
    SYNTHETIC_VALIDATION_CASES,
)
from predictor.services.feedback_learning import (
    execute_learning_batch,
    activate_learning_batch,
    train_adaptation_layer,
    compute_adaptation_delta,
    load_adaptation_model,
    verify_no_final_test_leakage,
    FinalTestLeakageError,
    MINIMUM_FEEDBACK_FOR_BATCH,
    MAX_DELTA_LOG_ODDS,
    ADAPTATION_FEATURE_NAMES,
    record_review_with_learning_signal,
)
from predictor.services.adapted_inference import (
    predict_adapted,
    compare_case_across_versions,
)
from predictor.services.screening_inference import (
    predict_screening,
    FROZEN_DECISION_THRESHOLD,
    EXPECTED_GAM_SHA256,
    get_artifact_paths,
)


class FeedbackTaxonomyTests(TestCase):
    """Tests for Master Feedback Taxonomy v1.0."""

    def test_taxonomy_version(self):
        self.assertEqual(get_taxonomy_version(), "1.0")

    def test_categories_loaded(self):
        active_cats = get_active_categories()
        self.assertGreaterEqual(len(active_cats), 10)

    def test_category_lookup(self):
        cat = get_category("bmi_overweighted")
        self.assertIsNotNone(cat)
        self.assertEqual(cat.learning_direction, DIR_REDUCE_INFLUENCE)
        self.assertIn("bmi", cat.relevant_features)

    def test_unmapped_category_produces_no_learning(self):
        cat = get_category("unmapped")
        self.assertIsNotNone(cat)
        self.assertEqual(cat.learning_direction, DIR_NO_LEARNING)
        self.assertEqual(len(cat.relevant_features), 0)

    def test_relevant_features_are_subset_of_stage1(self):
        for cat in get_active_categories():
            for feat in cat.relevant_features:
                self.assertIn(feat, STAGE1_FEATURES)


class FeedbackNLPTests(TestCase):
    """Tests for NLP feedback interpretation."""

    def test_empty_or_whitespace_text(self):
        result = interpret_feedback_text("")
        self.assertEqual(result.detected_category, "unmapped")
        self.assertEqual(result.confidence, 0.0)

    def test_interpreting_relevant_feedback(self):
        result = interpret_feedback_text("BMI is too heavily weighted for this patient")
        self.assertIsInstance(result, FeedbackNLPResult)
        self.assertIn(result.detected_category, [c.category_id for c in get_active_categories()])
        self.assertGreater(result.confidence, 0.0)

    def test_interpretation_returns_dict(self):
        result = interpret_feedback_text("Age alone should not trigger referral")
        d = result.to_dict()
        self.assertIn("detected_category", d)
        self.assertIn("confidence", d)
        self.assertIn("method", d)


class SimilarityServiceTests(TestCase):
    """Tests for the normalized Euclidean distance similarity metric."""

    def setUp(self):
        self.case_a = {
            'age': 55,
            'sex': 'female',
            'bmi': 31.2,
            'waist_cm': 94.0,
            'hypertension_history': 'yes',
            'smoking_history': 'no',
            'sedentary_minutes_day': 360,
        }
        self.case_b_identical = self.case_a.copy()
        self.case_c_different = {
            'age': 20,
            'sex': 'male',
            'bmi': 19.5,
            'waist_cm': 72.0,
            'hypertension_history': 'no',
            'smoking_history': 'yes',
            'sedentary_minutes_day': 60,
        }

    def test_identical_cases_similarity(self):
        sim = compute_similarity(self.case_a, self.case_b_identical)
        self.assertAlmostEqual(sim.similarity_score, 1.0, places=4)
        self.assertTrue(sim.is_similar)

    def test_dissimilar_cases_similarity(self):
        sim = compute_similarity(self.case_a, self.case_c_different)
        self.assertLess(sim.similarity_score, DEFAULT_SIMILARITY_THRESHOLD)
        self.assertFalse(sim.is_similar)

    def test_hba1c_not_in_similarity_features(self):
        sim = compute_similarity(self.case_a, self.case_b_identical)
        self.assertNotIn("hba1c", sim.features_used)
        self.assertNotIn("hba1c_percent", sim.features_used)


class ModelVersioningServiceTests(TestCase):
    """Tests for ModelVersion lifecycle and active version management."""

    def test_baseline_version_initialization(self):
        baseline = get_baseline_version()
        self.assertEqual(baseline.version_label, BASELINE_VERSION_LABEL)
        self.assertTrue(baseline.is_baseline)
        self.assertTrue(baseline.is_active)
        self.assertEqual(baseline.version_type, "baseline")

    def test_exactly_one_active_version(self):
        get_baseline_version()
        active_count = ModelVersion.objects.filter(is_active=True).count()
        self.assertEqual(active_count, 1)


class FeedbackLearningServiceTests(TestCase):
    """Tests for Feedback Learning Service & batch constraints."""

    def setUp(self):
        self.feedbacks = []
        for i in range(3):
            rec = ScreeningRecord.objects.create(
                age=50 + i,
                sex='female',
                bmi=Decimal(str(30.0 + i)),
                waist_cm=Decimal("95.0"),
                hypertension_history='yes',
                smoking_history='no',
                sedentary_minutes_day=400,
                screening_probability=0.25,
                ai_referral_recommended=True,
                model_name="GAM (Spline)",
                model_sha256="test_sha",
                preprocessor_sha256="test_prep_sha",
            )
            rev = HumanReview.objects.create(
                screening_record=rec,
                review_action='overridden',
                final_referral_recommended=False,
                reviewer_code="REV01",
                override_reason_code="clinical_judgment",
            )
            fb = HumanFeedback.objects.create(
                human_review=rev,
                structured_category="bmi_overweighted",
                relevant_feature="bmi",
                feedback_direction=DIR_REDUCE_INFLUENCE,
                is_eligible_for_learning=True,
                learning_status='pending',
                model_version_at_feedback=BASELINE_VERSION_LABEL,
                taxonomy_version="1.0",
            )
            self.feedbacks.append(fb)

    def test_batch_training_requires_minimum_feedback(self):
        HumanFeedback.objects.all().delete()
        res = execute_learning_batch()
        self.assertFalse(res['success'])
        self.assertIn("Insufficient", res['error'])

    def test_batch_training_and_candidate_creation(self):
        res = execute_learning_batch()
        self.assertTrue(res['success'], msg=f"Error: {res.get('error')}")
        self.assertIn("candidate_label", res)

        # Verify candidate exists and validation passed
        batch = FeedbackLearningBatch.objects.get(id=res['batch_id'])
        self.assertEqual(batch.status, "validating")
        self.assertEqual(batch.candidate_version.validation_status, "passed")

        # Baseline should still be active (activation is explicit!)
        active = get_active_version()
        self.assertTrue(active.is_baseline)

        # Explicitly activate candidate
        act_res = activate_learning_batch(str(batch.id))
        self.assertTrue(act_res['success'])

        new_active = get_active_version()
        self.assertFalse(new_active.is_baseline)
        self.assertEqual(new_active.version_label, batch.candidate_version.version_label)

        # Rollback test
        rollback_to_version(BASELINE_VERSION_LABEL)
        rolled_back_active = get_active_version()
        self.assertTrue(rolled_back_active.is_baseline)


class TechnicalValidationChecksTests(TestCase):
    """
    Tests for Part 4 Technical Validation.
    Verifies that all 13 executable validation checks execute and pass.
    """

    def setUp(self):
        self.feedbacks = []
        for i in range(3):
            rec = ScreeningRecord.objects.create(
                age=52 + i,
                sex='male',
                bmi=Decimal(str(29.0 + i)),
                waist_cm=Decimal("96.0"),
                hypertension_history='yes',
                smoking_history='no',
                sedentary_minutes_day=450,
                screening_probability=0.28,
                ai_referral_recommended=True,
                model_name="GAM (Spline)",
                model_sha256="test_sha",
                preprocessor_sha256="test_prep_sha",
            )
            rev = HumanReview.objects.create(
                screening_record=rec,
                review_action='overridden',
                final_referral_recommended=False,
                reviewer_code="DOC_TEST",
                override_reason_code="clinical_judgment",
            )
            fb = HumanFeedback.objects.create(
                human_review=rev,
                structured_category="bmi_overweighted",
                relevant_feature="bmi",
                feedback_direction=DIR_REDUCE_INFLUENCE,
                is_eligible_for_learning=True,
                learning_status='pending',
                model_version_at_feedback=BASELINE_VERSION_LABEL,
                taxonomy_version="1.0",
            )
            self.feedbacks.append(fb)

    def test_all_13_validation_checks_pass(self):
        """Verify that training a candidate runs and passes all 13 executable validation checks."""
        training_result = train_adaptation_layer(self.feedbacks)
        self.assertTrue(training_result.success)

        candidate = create_candidate_version(
            parent_label=BASELINE_VERSION_LABEL,
            candidate_label="GAM-v2-test-candidate",
            adaptation_path=training_result.artifact_path,
            feedback_count=training_result.feedback_count,
        )

        passed = validate_candidate(candidate.version_label)
        self.assertTrue(passed)

        candidate.refresh_from_db()
        self.assertEqual(candidate.validation_status, "passed")
        checks = candidate.validation_metrics.get("checks", [])
        self.assertEqual(len(checks), 13, msg=f"Expected 13 checks, got {len(checks)}")

        # Verify each individual check passed
        check_names = {c["check"] for c in checks}
        expected_check_names = {
            "artifact_exists",
            "artifact_loads_successfully",
            "artifact_sha256_matches",
            "model_input_dimensions_correct",
            "expected_feature_names_present",
            "repeatable_deterministic_inference",
            "output_probabilities_in_range",
            "actual_adaptation_deltas_bounded",
            "frozen_gam_hash_unchanged",
            "threshold_remains_exact",
            "dual_outputs_produced",
            "historical_records_unmutated",
            "frozen_gam_artifact_unmodified",
        }
        self.assertEqual(check_names, expected_check_names)
        for c in checks:
            self.assertTrue(c["passed"], msg=f"Check failed: {c['check']}")


class FinalTestLeakageProtectionTests(TestCase):
    """
    Tests for Part 5 Final-Test Leakage Protection.
    Verifies that observations from N=812 final-test set cannot enter the learning loop.
    """

    def test_non_final_test_records_pass_leakage_check(self):
        """Normal synthetic records pass the leakage check."""
        rec = ScreeningRecord.objects.create(
            age=55,
            sex='male',
            bmi=Decimal('32.1'),
            waist_cm=Decimal('105.0'),
            hypertension_history='yes',
            smoking_history='yes',
            sedentary_minutes_day=600,
            screening_probability=0.34,
            ai_referral_recommended=True,
            model_name="GAM",
            model_sha256="test",
            preprocessor_sha256="test",
        )
        rev = HumanReview.objects.create(
            screening_record=rec,
            review_action='overridden',
            final_referral_recommended=False,
            reviewer_code="DOC",
            override_reason_code="clinical_judgment",
        )
        fb = HumanFeedback.objects.create(
            human_review=rev,
            structured_category="bmi_overweighted",
            relevant_feature="bmi",
            feedback_direction=DIR_REDUCE_INFLUENCE,
            is_eligible_for_learning=True,
            learning_status='pending',
            model_version_at_feedback=BASELINE_VERSION_LABEL,
            taxonomy_version="1.0",
        )
        ok, msg = verify_no_final_test_leakage([fb])
        self.assertTrue(ok)

    def test_final_test_signature_leakage_raises_error(self):
        """A record matching a canonical final-test observation feature signature raises FinalTestLeakageError."""
        # Final test participant SEQN 130379 features from analytic_expanded_complete.parquet:
        # age=66, sex=female (2.0), bmi=31.2, waist_cm=107.0, hyp=no, smk=no, sed=480
        # Let's use SEQN 130391: age=33, sex=female, bmi=31.2, waist=107.0, hyp=no, smk=no, sed=600
        rec_leaked = ScreeningRecord.objects.create(
            age=33,
            sex='female',
            bmi=Decimal('31.2'),
            waist_cm=Decimal('107.0'),
            hypertension_history='no',
            smoking_history='no',
            sedentary_minutes_day=600,
            screening_probability=0.20,
            ai_referral_recommended=True,
            model_name="GAM",
            model_sha256="test",
            preprocessor_sha256="test",
        )
        rev_leaked = HumanReview.objects.create(
            screening_record=rec_leaked,
            review_action='overridden',
            final_referral_recommended=False,
            reviewer_code="DOC",
            override_reason_code="clinical_judgment",
        )
        fb_leaked = HumanFeedback.objects.create(
            human_review=rev_leaked,
            structured_category="bmi_overweighted",
            relevant_feature="bmi",
            feedback_direction=DIR_REDUCE_INFLUENCE,
            is_eligible_for_learning=True,
            learning_status='pending',
            model_version_at_feedback=BASELINE_VERSION_LABEL,
            taxonomy_version="1.0",
        )

        with self.assertRaises(FinalTestLeakageError):
            verify_no_final_test_leakage([fb_leaked])

    def test_final_test_seqn_in_token_raises_error(self):
        """A record with a final-test SEQN in its token raises FinalTestLeakageError."""
        rec_token = ScreeningRecord.objects.create(
            age=40,
            sex='male',
            bmi=Decimal('25.0'),
            waist_cm=Decimal('85.0'),
            hypertension_history='no',
            smoking_history='no',
            sedentary_minutes_day=300,
            screening_probability=0.10,
            ai_referral_recommended=False,
            model_name="GAM",
            model_sha256="test",
            preprocessor_sha256="test",
            idempotency_token="SEQN_130379_token",
        )
        rev = HumanReview.objects.create(
            screening_record=rec_token,
            review_action='overridden',
            final_referral_recommended=True,
            reviewer_code="DOC",
            override_reason_code="clinical_judgment",
        )
        fb = HumanFeedback.objects.create(
            human_review=rev,
            structured_category="increase_risk_general",
            relevant_feature=None,
            feedback_direction=DIR_INCREASE_GLOBAL,
            is_eligible_for_learning=True,
            learning_status='pending',
            model_version_at_feedback=BASELINE_VERSION_LABEL,
            taxonomy_version="1.0",
        )

        with self.assertRaises(FinalTestLeakageError):
            verify_no_final_test_leakage([fb])


class FeedbackDirectionSemanticsTests(TestCase):
    """
    Tests for Part 9: Multiple Feedback Directions.
    Verifies that the adaptation model responds appropriately to:
    1. Feature-specific reduce influence (bmi_overweighted)
    2. Feature-specific increase influence (bmi_underweighted)
    3. Global reduce-risk feedback
    4. Global increase-risk feedback
    5. Contextual override
    6. No-learning feedback
    """

    def _create_and_train_batch(self, category: str, feature: str, direction: str, override_to: bool):
        feedbacks = []
        for i in range(3):
            rec = ScreeningRecord.objects.create(
                age=50 + i,
                sex='male',
                bmi=Decimal(str(32.0 + i * 0.5)),
                waist_cm=Decimal("100.0"),
                hypertension_history='yes',
                smoking_history='yes',
                sedentary_minutes_day=500,
                screening_probability=0.30,
                ai_referral_recommended=True,
                model_name="GAM",
                model_sha256="test",
                preprocessor_sha256="test",
            )
            rev = HumanReview.objects.create(
                screening_record=rec,
                review_action='overridden',
                final_referral_recommended=override_to,
                reviewer_code="DOC",
                override_reason_code="clinical_judgment",
            )
            fb = HumanFeedback.objects.create(
                human_review=rev,
                structured_category=category,
                relevant_feature=feature,
                feedback_direction=direction,
                is_eligible_for_learning=True,
                learning_status='pending',
                model_version_at_feedback=BASELINE_VERSION_LABEL,
                taxonomy_version="1.0",
            )
            feedbacks.append(fb)

        result = train_adaptation_layer(feedbacks)
        self.assertTrue(result.success)
        return load_adaptation_model(result.artifact_path)

    def test_1_feature_specific_reduce_influence(self):
        """bmi_overweighted produces negative weight on BMI and negative delta on high-BMI case."""
        artifact = self._create_and_train_batch("bmi_overweighted", "bmi", DIR_REDUCE_INFLUENCE, False)
        test_case = {"age": 55, "sex": "male", "bmi": 32.0, "waist_cm": 100.0, "hypertension_history": "yes", "smoking_history": "yes", "sedentary_minutes_day": 500}
        delta = compute_adaptation_delta(artifact, test_case)
        self.assertLess(delta, 0.0)
        self.assertLess(artifact["weights"]["bmi"], 0.0)

    def test_2_feature_specific_increase_influence(self):
        """bmi_underweighted produces positive weight on BMI and positive delta on high-BMI case."""
        artifact = self._create_and_train_batch("bmi_underweighted", "bmi", DIR_INCREASE_INFLUENCE, True)
        test_case = {"age": 55, "sex": "male", "bmi": 32.0, "waist_cm": 100.0, "hypertension_history": "yes", "smoking_history": "yes", "sedentary_minutes_day": 500}
        delta = compute_adaptation_delta(artifact, test_case)
        self.assertGreater(delta, 0.0)
        self.assertGreater(artifact["weights"]["bmi"], 0.0)

    def test_3_global_reduce_risk(self):
        """DIR_REDUCE_GLOBAL produces negative weight on global_bias."""
        artifact = self._create_and_train_batch("reduce_risk_general", "", DIR_REDUCE_GLOBAL, False)
        test_case = {"age": 50, "sex": "female", "bmi": 28.0, "waist_cm": 88.0, "hypertension_history": "no", "smoking_history": "no", "sedentary_minutes_day": 300}
        delta = compute_adaptation_delta(artifact, test_case)
        self.assertLess(delta, 0.0)
        self.assertLess(artifact["weights"]["global_bias"], 0.0)

    def test_4_global_increase_risk(self):
        """DIR_INCREASE_GLOBAL produces positive weight on global_bias."""
        artifact = self._create_and_train_batch("increase_risk_general", "", DIR_INCREASE_GLOBAL, True)
        test_case = {"age": 50, "sex": "female", "bmi": 28.0, "waist_cm": 88.0, "hypertension_history": "no", "smoking_history": "no", "sedentary_minutes_day": 300}
        delta = compute_adaptation_delta(artifact, test_case)
        self.assertGreater(delta, 0.0)
        self.assertGreater(artifact["weights"]["global_bias"], 0.0)

    def test_5_contextual_override(self):
        """DIR_CONTEXTUAL derives direction from override (AI=refer, override=no refer -> negative)."""
        artifact = self._create_and_train_batch("contextual_override", "", DIR_CONTEXTUAL, False)
        test_case = {"age": 55, "sex": "male", "bmi": 32.0, "waist_cm": 100.0, "hypertension_history": "yes", "smoking_history": "yes", "sedentary_minutes_day": 500}
        delta = compute_adaptation_delta(artifact, test_case)
        self.assertLess(delta, 0.0)

    def test_6_no_learning_feedback(self):
        """DIR_NO_LEARNING produces zero weights and zero delta."""
        artifact = self._create_and_train_batch("unmapped", "", DIR_NO_LEARNING, False)
        test_case = {"age": 55, "sex": "male", "bmi": 32.0, "waist_cm": 100.0, "hypertension_history": "yes", "smoking_history": "yes", "sedentary_minutes_day": 500}
        delta = compute_adaptation_delta(artifact, test_case)
        self.assertEqual(delta, 0.0)
        for w in artifact["weights"].values():
            self.assertEqual(w, 0.0)


class CaseAToCaseBExperimentTests(TestCase):
    """
    Controlled Experiment from Part 8:
    Case A → Human Review → Structured Feedback (bmi_overweighted) → Batch Update
    → Validate Candidate → Activate → Case B Inference.
    """

    def test_reproducible_case_a_to_case_b_experiment(self):
        # 1. CASE A
        case_a_data = {
            'age': 55,
            'sex': 'male',
            'bmi': Decimal('32.1'),
            'waist_cm': Decimal('105.0'),
            'hypertension_history': 'yes',
            'smoking_history': 'yes',
            'sedentary_minutes_day': 600,
        }

        pred_a = predict_screening(case_a_data)
        self.assertTrue(pred_a.referral_recommended)
        self.assertAlmostEqual(pred_a.probability, 0.341141, places=3)

        rec_a = ScreeningRecord.objects.create(
            age=case_a_data['age'],
            sex=case_a_data['sex'],
            bmi=case_a_data['bmi'],
            waist_cm=case_a_data['waist_cm'],
            hypertension_history=case_a_data['hypertension_history'],
            smoking_history=case_a_data['smoking_history'],
            sedentary_minutes_day=case_a_data['sedentary_minutes_day'],
            screening_probability=pred_a.probability,
            ai_referral_recommended=pred_a.referral_recommended,
            model_name="Phase-5 GAM (λ=10.0, Splines=10)",
            model_sha256=EXPECTED_GAM_SHA256,
            preprocessor_sha256="test",
        )

        # 2. Human Review: Clinician overrides referral to False
        rev_a = HumanReview.objects.create(
            screening_record=rec_a,
            review_action='overridden',
            final_referral_recommended=False,
            reviewer_code="DOC_EXP_01",
            override_reason_code="clinical_judgment",
        )

        # 3. Human Feedback: bmi_overweighted (relevant_feature=bmi, reduce_influence)
        fb_a = HumanFeedback.objects.create(
            human_review=rev_a,
            structured_category="bmi_overweighted",
            relevant_feature="bmi",
            feedback_direction=DIR_REDUCE_INFLUENCE,
            is_eligible_for_learning=True,
            learning_status='pending',
            model_version_at_feedback=BASELINE_VERSION_LABEL,
            taxonomy_version="1.0",
        )

        # Add 2 more similar feedbacks to meet minimum batch threshold (N=3)
        for i in [1, 2]:
            r = ScreeningRecord.objects.create(
                age=54 + i,
                sex='male',
                bmi=Decimal(str(32.0 + i * 0.3)),
                waist_cm=Decimal('104.0'),
                hypertension_history='yes',
                smoking_history='yes',
                sedentary_minutes_day=590,
                screening_probability=pred_a.probability,
                ai_referral_recommended=True,
                model_name="Phase-5 GAM (λ=10.0, Splines=10)",
                model_sha256=EXPECTED_GAM_SHA256,
                preprocessor_sha256="test",
            )
            rv = HumanReview.objects.create(
                screening_record=r,
                review_action='overridden',
                final_referral_recommended=False,
                reviewer_code=f"DOC_EXP_0{i+1}",
                override_reason_code="clinical_judgment",
            )
            HumanFeedback.objects.create(
                human_review=rv,
                structured_category='bmi_overweighted',
                relevant_feature='bmi',
                feedback_direction=DIR_REDUCE_INFLUENCE,
                is_eligible_for_learning=True,
                learning_status='pending',
                model_version_at_feedback=BASELINE_VERSION_LABEL,
                taxonomy_version="1.0",
            )

        # 4. Learning Batch: Trigger batch learning
        batch_res = execute_learning_batch()
        self.assertTrue(batch_res['success'])
        self.assertIsNotNone(batch_res['batch_id'])

        # Activate the candidate version
        act_res = activate_learning_batch(batch_res['batch_id'])
        self.assertTrue(act_res['success'])

        # 5. CASE B: Subsequent case with similar characteristics
        case_b_data = {
            'age': 53,
            'sex': 'male',
            'bmi': Decimal('31.5'),
            'waist_cm': Decimal('103.0'),
            'hypertension_history': 'yes',
            'smoking_history': 'yes',
            'sedentary_minutes_day': 580,
        }

        # Check similarity between Case A and Case B
        sim = compute_similarity(case_a_data, case_b_data)
        self.assertGreaterEqual(sim.similarity_score, 0.85)
        self.assertTrue(sim.is_similar)

        # Create ScreeningRecord for Case B
        pred_b_base = predict_screening(case_b_data)
        rec_b = ScreeningRecord.objects.create(
            age=case_b_data['age'],
            sex=case_b_data['sex'],
            bmi=case_b_data['bmi'],
            waist_cm=case_b_data['waist_cm'],
            hypertension_history=case_b_data['hypertension_history'],
            smoking_history=case_b_data['smoking_history'],
            sedentary_minutes_day=case_b_data['sedentary_minutes_day'],
            screening_probability=pred_b_base.probability,
            ai_referral_recommended=pred_b_base.referral_recommended,
            model_name="Phase-5 GAM (λ=10.0, Splines=10)",
            model_sha256=EXPECTED_GAM_SHA256,
            preprocessor_sha256="test",
        )

        # Case B inference using ONLY Case B's features (no Case A feedback metadata!)
        adapted_b = predict_adapted(case_b_data)
        self.assertTrue(adapted_b.has_adaptation)
        self.assertNotEqual(adapted_b.adapted_version_label, BASELINE_VERSION_LABEL)

        # Verify behavioral change:
        # BMI overweighted (reduce influence) causes delta_log_odds < 0
        # and adapted_probability < baseline_probability
        self.assertLess(adapted_b.delta_log_odds, 0.0)
        self.assertLess(adapted_b.adapted_probability, adapted_b.baseline_probability)
        self.assertLess(adapted_b.delta_probability, 0.0)

        # Threshold remains exactly 0.1389
        self.assertEqual(adapted_b.threshold, 0.1389)

        # Record SimilarCaseComparison
        active_v = get_active_version()
        batch_obj = FeedbackLearningBatch.objects.get(id=batch_res['batch_id'])
        comparison = SimilarCaseComparison.objects.create(
            source_case=rec_a,
            target_case=rec_b,
            similarity_score=sim.similarity_score,
            similarity_method=sim.method,
            similarity_features_used=sim.features_used,
            similarity_normalization_version=sim.normalization_bounds_version,
            baseline_version=get_baseline_version(),
            baseline_probability=adapted_b.baseline_probability,
            baseline_recommendation=adapted_b.baseline_recommendation,
            updated_version=active_v,
            updated_probability=adapted_b.adapted_probability,
            updated_recommendation=adapted_b.adapted_recommendation,
            probability_delta=adapted_b.delta_probability,
            recommendation_changed=adapted_b.recommendation_changed,
            feedback_category="bmi_overweighted",
            learning_batch=batch_obj,
        )
        self.assertIsNotNone(comparison.id)

        # Verify Historical Immutability: Case A original prediction was NOT changed!
        rec_a.refresh_from_db()
        self.assertEqual(rec_a.screening_probability, pred_a.probability)
        self.assertEqual(rec_a.ai_referral_recommended, pred_a.referral_recommended)
        self.assertEqual(rec_a.model_sha256, EXPECTED_GAM_SHA256)


class AuditTrailImmutabilityTests(TestCase):
    """
    Tests for Part 6 & Governance:
    Verifies that Case A original AI prediction remains strictly immutable
    across the entire lifecycle.
    """

    def test_case_a_prediction_never_mutated(self):
        rec_a = ScreeningRecord.objects.create(
            age=60,
            sex='male',
            bmi=Decimal('33.0'),
            waist_cm=Decimal('108.0'),
            hypertension_history='yes',
            smoking_history='yes',
            sedentary_minutes_day=650,
            screening_probability=0.45,
            ai_referral_recommended=True,
            decision_threshold=Decimal('0.1389'),
            model_name="Phase-5 GAM",
            model_sha256=EXPECTED_GAM_SHA256,
            preprocessor_sha256="test_sha",
        )

        orig_prob = rec_a.screening_probability
        orig_rec = rec_a.ai_referral_recommended
        orig_thresh = rec_a.decision_threshold
        orig_sha = rec_a.model_sha256

        # Human override
        rev = HumanReview.objects.create(
            screening_record=rec_a,
            review_action='overridden',
            final_referral_recommended=False,
            reviewer_code="DOC_AUDIT",
            override_reason_code="clinical_judgment",
        )

        # Feedback
        fb = HumanFeedback.objects.create(
            human_review=rev,
            structured_category="bmi_overweighted",
            relevant_feature="bmi",
            feedback_direction=DIR_REDUCE_INFLUENCE,
            is_eligible_for_learning=True,
            learning_status='pending',
            model_version_at_feedback=BASELINE_VERSION_LABEL,
            taxonomy_version="1.0",
        )

        rec_a.refresh_from_db()
        self.assertEqual(rec_a.screening_probability, orig_prob)
        self.assertEqual(rec_a.ai_referral_recommended, orig_rec)
        self.assertEqual(rec_a.decision_threshold, orig_thresh)
        self.assertEqual(rec_a.model_sha256, orig_sha)


class UnifiedHumanReviewAndLearningTests(TestCase):
    """
    Tests for the Unified Human Review & Feedback Architecture.
    Verifies:
    1. Human override itself is the intervention that generates the feedback.
    2. Single-step submission captures review decision, factor, and rationale.
    3. Eligible feedback is generated automatically in Feedback Lab mode.
    4. Evaluation mode participant data is strictly isolated (is_eligible=False).
    5. Practice records are strictly isolated (is_eligible=False).
    6. Non-corrective factors produce non-eligible feedback.
    7. No standalone feedback form or secondary submission step.
    """

    def setUp(self):
        self.client = Client()
        self.record = ScreeningRecord.objects.create(
            age=52,
            sex='male',
            bmi=Decimal('31.5'),
            waist_cm=Decimal('102.0'),
            hypertension_history='yes',
            smoking_history='no',
            sedentary_minutes_day=450,
            screening_probability=0.28,
            ai_referral_recommended=True,
            decision_threshold=Decimal('0.1389'),
            model_name="Phase-5 GAM",
            model_sha256=EXPECTED_GAM_SHA256,
            preprocessor_sha256="test_sha",
        )
        self.explanation = ScreeningExplanation.objects.create(
            screening_record=self.record,
            status='generated',
            intercept=-2.0,
            reconstructed_linear_predictor=-1.15,
            reconstructed_probability=0.24,
            contributions_json=[
                {"feature_name": "bmi", "display_name": "BMI", "formatted_value": "31.5", "contribution": 0.85, "direction": "higher"},
            ],
            reconstruction_error=0.001,
            model_sha256=EXPECTED_GAM_SHA256,
        )

    def test_override_creates_review_and_feedback_single_action(self):
        """Human override atomically generates both HumanReview and canonical HumanFeedback."""
        review, feedback = record_review_with_learning_signal(
            screening_record=self.record,
            reviewer_code="CLINICIAN_01",
            human_decision="override",
            override_factor="bmi_overweighted",
            rationale="BMI is elevated due to muscular build, not adiposity.",
        )

        self.assertIsNotNone(review)
        self.assertEqual(review.review_action, "overridden")
        # Final decision is opposite of AI recommendation (True -> False)
        self.assertFalse(review.final_referral_recommended)
        self.assertEqual(review.override_reason_code, "bmi_overweighted")
        self.assertEqual(review.override_note, "BMI is elevated due to muscular build, not adiposity.")

        self.assertIsNotNone(feedback)
        self.assertEqual(feedback.human_review, review)
        self.assertEqual(feedback.structured_category, "bmi_overweighted")
        self.assertEqual(feedback.relevant_feature, "bmi")
        self.assertEqual(feedback.feedback_direction, DIR_REDUCE_INFLUENCE)
        self.assertTrue(feedback.is_eligible_for_learning)
        self.assertEqual(feedback.learning_status, "pending")
        self.assertEqual(feedback.feedback_text, "BMI is elevated due to muscular build, not adiposity.")
        self.assertIsNotNone(feedback.nlp_raw_output)

    def test_accept_derives_decision_and_no_corrective_signal(self):
        """Accepting AI recommendation derives decision from AI output and produces no corrective learning signal."""
        review, feedback = record_review_with_learning_signal(
            screening_record=self.record,
            reviewer_code="CLINICIAN_02",
            human_decision="accept",
        )

        self.assertIsNotNone(review)
        self.assertEqual(review.review_action, "accepted")
        # Final decision matches AI recommendation (True -> True)
        self.assertTrue(review.final_referral_recommended)
        self.assertIsNone(review.override_reason_code)

        # No corrective feedback generated
        if feedback is not None:
            self.assertFalse(feedback.is_eligible_for_learning)
            self.assertEqual(feedback.learning_status, "excluded")

    def test_evaluation_mode_participant_isolation(self):
        """In evaluation mode, overrides never generate active learning signals."""
        from django.conf import settings
        original_mode = getattr(settings, 'APP_MODE', 'feedback_lab')
        try:
            settings.APP_MODE = 'evaluation'
            review, feedback = record_review_with_learning_signal(
                screening_record=self.record,
                reviewer_code="PARTICIPANT_99",
                human_decision="override",
                override_factor="bmi_overweighted",
                rationale="Evaluation override test",
            )
            self.assertIsNotNone(feedback)
            self.assertFalse(feedback.is_eligible_for_learning)
            self.assertEqual(feedback.learning_status, "excluded")
        finally:
            settings.APP_MODE = original_mode

    def test_practice_record_isolation(self):
        """Practice cases (P0) never generate active learning signals."""
        self.record.is_practice = True
        self.record.save()

        review, feedback = record_review_with_learning_signal(
            screening_record=self.record,
            reviewer_code="TRAINEE_01",
            human_decision="override",
            override_factor="waist_overweighted",
            rationale="Practice exercise",
        )
        self.assertIsNotNone(feedback)
        self.assertFalse(feedback.is_eligible_for_learning)
        self.assertEqual(feedback.learning_status, "excluded")

    def test_non_corrective_factor_not_eligible(self):
        """Non-learning signal overrides are excluded from candidate adaptation training."""
        review, feedback = record_review_with_learning_signal(
            screening_record=self.record,
            reviewer_code="CLINICIAN_03",
            human_decision="override",
            override_factor="no_learning_signal",
            rationale="Disagreement without directional feature guidance",
        )
        self.assertIsNotNone(feedback)
        self.assertFalse(feedback.is_eligible_for_learning)
        self.assertEqual(feedback.learning_status, "excluded")

    def test_unified_review_view_post_and_template_render(self):
        """Test POST to unified_review_view and verify template renders finalized state without standalone feedback card."""
        url = reverse('predictor:unified_review', kwargs={'screening_id': self.record.id})
        response = self.client.post(url, {
            'reviewer_code': 'DOC_UNIFIED',
            'human_decision': 'override',
            'override_factor': 'bmi_overweighted',
            'rationale': 'Unified workflow test note',
        })
        self.assertEqual(response.status_code, 302)

        # Refresh and check review
        self.record.refresh_from_db()
        self.assertTrue(hasattr(self.record, 'human_review'))
        rev = self.record.human_review
        self.assertEqual(rev.review_action, 'overridden')
        self.assertEqual(rev.reviewer_code, 'DOC_UNIFIED')
        self.assertTrue(hasattr(rev, 'feedback'))
        self.assertTrue(rev.feedback.is_eligible_for_learning)

        # Follow redirect to screening_result page
        result_url = reverse('predictor:screening_result', kwargs={'screening_id': self.record.id})
        get_response = self.client.get(result_url)
        self.assertEqual(get_response.status_code, 200)

        content = get_response.content.decode('utf-8')
        # Finalized review card must be present
        self.assertIn('id="human-review-card-finalized"', content)
        # Status badge for feedback signal must be present
        self.assertIn('Feedback Signal Recorded (Eligible for Learning)', content)
        # Link to experiment must be present
        self.assertIn('View in Feedback Lab Experiment', content)
        # Standalone feedback submission card must NOT be present
        self.assertNotIn('id="feedback-submission-card"', content)
        self.assertNotIn('Provide Feedback for Learning Loop (Optional)', content)

