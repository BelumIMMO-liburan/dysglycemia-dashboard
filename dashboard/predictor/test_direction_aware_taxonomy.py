"""
Tests for Direction-Aware Human Override & Feedback Taxonomy (Taxonomy v2.0).

Verifies all 22 requirements from Part 7 of the research governance specification:
  A. Evaluation taxonomy (items 1-5)
  B. Canonical signal parsing (items 6-10)
  C. Directionality (items 11-14)
  D. Backward compatibility (items 15-17)
  E. Safety and isolation (items 18-22)
"""

import hashlib
from decimal import Decimal
from pathlib import Path

from django.conf import settings
from django.test import TestCase
from django.urls import reverse

from predictor.models import (
    ScreeningRecord,
    ScreeningExplanation,
    HumanReview,
    HumanFeedback,
)
from predictor.services.feedback_taxonomy import (
    TAXONOMY_VERSION,
    get_taxonomy_version,
    get_category,
    get_active_categories,
    parse_canonical_signal,
    canonical_signal_to_learning_fields,
    CanonicalLearningSignal,
    NULL_SIGNAL,
    DIR_REDUCE_INFLUENCE,
    DIR_INCREASE_INFLUENCE,
    DIR_NO_LEARNING,
    STAGE1_FEATURES,
)
from predictor.services.feedback_learning import (
    record_review_with_learning_signal,
    collect_eligible_feedback,
    train_adaptation_layer,
    _build_training_row,
    start_controlled_experiment,
    run_controlled_learning,
    activate_controlled_adaptation,
    evaluate_controlled_case_b,
    ADAPTATION_FEATURE_NAMES,
)
from predictor.services.screening_inference import (
    FROZEN_DECISION_THRESHOLD,
    EXPECTED_GAM_SHA256,
    get_artifact_paths,
)


class EvaluationTaxonomyGovernanceTests(TestCase):
    """Part 7A: Evaluation Mode Taxonomy & UI Governance (Tests 1-5)."""

    def setUp(self):
        self.record = ScreeningRecord.objects.create(
            age=55,
            sex='male',
            bmi=Decimal('32.1'),
            waist_cm=Decimal('105.0'),
            hypertension_history='yes',
            smoking_history='yes',
            sedentary_minutes_day=600,
            screening_probability=0.341141,
            ai_referral_recommended=True,
            decision_threshold=Decimal('0.1389'),
            model_name="Phase-5 GAM",
            model_sha256=EXPECTED_GAM_SHA256,
            preprocessor_sha256="preprocessor_sha",
        )
        self.explanation = ScreeningExplanation.objects.create(
            screening_record=self.record,
            status='generated',
            intercept=-2.0,
            reconstructed_linear_predictor=-0.65,
            reconstructed_probability=0.341141,
            contributions_json=[
                {"feature_name": "bmi", "display_name": "BMI", "formatted_value": "32.1", "contribution": 0.85, "direction": "higher"},
            ],
            reconstruction_error=0.0001,
            model_sha256=EXPECTED_GAM_SHA256,
        )

    def test_1_evaluation_ui_renders_human_override_rationale(self):
        """1. Evaluation UI renders 'Human Override Rationale' and audit notice."""
        original_mode = getattr(settings, 'APP_MODE', 'feedback_lab')
        try:
            settings.APP_MODE = 'evaluation'
            url = reverse('predictor:screening_result', kwargs={'screening_id': self.record.id})
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
            content = response.content.decode('utf-8')

            # Must render Evaluation Dashboard specific labels
            self.assertIn("Human Override Rationale", content)
            self.assertIn("This rationale is recorded for audit and research analysis only", content)
            # Must NOT render Feedback Lab learning signal header in Evaluation Mode
            self.assertNotIn("Step A: Which factor is involved?", content)
            self.assertNotIn("Step B: What direction of adjustment is intended?", content)
        finally:
            settings.APP_MODE = original_mode

    def test_2_clinical_override_wording_removed_from_ui(self):
        """2. 'Clinical Override' and 'Clinical Rationale' wording is replaced with non-clinical terms."""
        url = reverse('predictor:screening_result', kwargs={'screening_id': self.record.id})
        response = self.client.get(url)
        content = response.content.decode('utf-8')

        # Wording must use Human Override / Decision Rationale
        self.assertNotIn("Clinical Override", content)
        self.assertNotIn("Clinical Rationale", content)
        self.assertIn("human override", content.lower())
        self.assertIn("Decision Rationale", content)

    def test_3_evaluation_rationale_submission_does_not_trigger_learning(self):
        """3. In evaluation mode, override rationale submissions never become eligible learning signals."""
        original_mode = getattr(settings, 'APP_MODE', 'feedback_lab')
        try:
            settings.APP_MODE = 'evaluation'
            review, feedback = record_review_with_learning_signal(
                screening_record=self.record,
                reviewer_code="EVAL_PARTICIPANT_01",
                human_decision="override",
                override_factor="bmi_overweighted",
                rationale="Audit rationale only",
            )
            self.assertIsNotNone(review)
            self.assertEqual(review.review_action, "overridden")
            self.assertIsNotNone(feedback)
            # Must NOT be eligible for learning
            self.assertFalse(feedback.is_eligible_for_learning)
            self.assertEqual(feedback.learning_status, "excluded")
        finally:
            settings.APP_MODE = original_mode

    def test_4_evaluation_rationale_cannot_modify_model_parameters(self):
        """4. Submitting an evaluation override cannot modify model weights or trigger adaptation."""
        original_mode = getattr(settings, 'APP_MODE', 'feedback_lab')
        try:
            settings.APP_MODE = 'evaluation'
            record_review_with_learning_signal(
                screening_record=self.record,
                reviewer_code="EVAL_PARTICIPANT_02",
                human_decision="override",
                override_factor="waist_overweighted",
                rationale="Audit rationale test",
            )
            # Eligible feedback list must be completely empty
            eligible = collect_eligible_feedback()
            self.assertEqual(len(eligible), 0)

            # Training with empty feedback must fail safely
            result = train_adaptation_layer(eligible)
            self.assertFalse(result.success)
        finally:
            settings.APP_MODE = original_mode

    def test_5_evaluation_mode_blocks_feedback_lab_endpoints(self):
        """5. Evaluation mode blocks access to Feedback Lab endpoints (returns HTTP 403)."""
        original_mode = getattr(settings, 'APP_MODE', 'feedback_lab')
        try:
            settings.APP_MODE = 'evaluation'
            url = reverse('predictor:feedback_experiment')
            response = self.client.get(url)
            self.assertEqual(response.status_code, 403)

            url_start = reverse('predictor:start_controlled_experiment')
            res_start = self.client.post(url_start)
            self.assertEqual(res_start.status_code, 403)
        finally:
            settings.APP_MODE = original_mode


class CanonicalSignalParsingTests(TestCase):
    """Part 7B: Canonical Signal Parsing (Tests 6-10)."""

    def test_6_legacy_bmi_overweighted_maps_to_bmi_reduce(self):
        """6. bmi_overweighted maps to target_feature=bmi, direction=reduce, scope=feature_specific."""
        signal = parse_canonical_signal(category_id="bmi_overweighted")
        self.assertEqual(signal.target_feature, "bmi")
        self.assertEqual(signal.direction, "reduce")
        self.assertEqual(signal.scope, "feature_specific")
        self.assertTrue(signal.is_actionable)
        self.assertTrue(signal.is_directional)

    def test_7_legacy_age_overweighted_maps_to_age_reduce(self):
        """7. age_overweighted maps to target_feature=age, direction=reduce, scope=feature_specific."""
        signal = parse_canonical_signal(category_id="age_overweighted")
        self.assertEqual(signal.target_feature, "age")
        self.assertEqual(signal.direction, "reduce")
        self.assertEqual(signal.scope, "feature_specific")
        self.assertTrue(signal.is_actionable)

    def test_8_no_learning_signal_maps_to_none_none(self):
        """8. no_learning_signal maps to target_feature=none, direction=none, scope=none."""
        signal = parse_canonical_signal(category_id="no_learning_signal")
        self.assertEqual(signal.target_feature, "none")
        self.assertEqual(signal.direction, "none")
        self.assertEqual(signal.scope, "none")
        self.assertFalse(signal.is_actionable)
        self.assertFalse(signal.is_directional)

    def test_9_new_bmi_reduce_signal_maps_correctly(self):
        """9. Explicit BMI-reduce signal maps correctly."""
        signal = parse_canonical_signal(
            target_feature="bmi",
            direction="reduce",
            scope="feature_specific",
        )
        self.assertEqual(signal.target_feature, "bmi")
        self.assertEqual(signal.direction, "reduce")
        self.assertEqual(signal.scope, "feature_specific")
        self.assertTrue(signal.is_actionable)
        self.assertTrue(signal.is_directional)

        fields = canonical_signal_to_learning_fields(signal)
        self.assertEqual(fields["relevant_feature"], "bmi")
        self.assertEqual(fields["feedback_direction"], DIR_REDUCE_INFLUENCE)

    def test_10_new_bmi_increase_signal_maps_correctly(self):
        """10. Explicit BMI-increase signal maps correctly."""
        signal = parse_canonical_signal(
            target_feature="bmi",
            direction="increase",
            scope="feature_specific",
        )
        self.assertEqual(signal.target_feature, "bmi")
        self.assertEqual(signal.direction, "increase")
        self.assertEqual(signal.scope, "feature_specific")
        self.assertTrue(signal.is_actionable)
        self.assertTrue(signal.is_directional)

        fields = canonical_signal_to_learning_fields(signal)
        self.assertEqual(fields["relevant_feature"], "bmi")
        self.assertEqual(fields["feedback_direction"], DIR_INCREASE_INFLUENCE)


class DirectionalityAndIsolationTests(TestCase):
    """Part 7C: Directionality & Feature Isolation (Tests 11-14)."""

    def setUp(self):
        self.screening = ScreeningRecord.objects.create(
            age=55,
            sex='male',
            bmi=Decimal('32.0'),
            waist_cm=Decimal('100.0'),
            hypertension_history='yes',
            smoking_history='yes',
            sedentary_minutes_day=500,
            screening_probability=0.30,
            ai_referral_recommended=True,
            model_name="GAM",
            model_sha256="test",
            preprocessor_sha256="test",
        )

    def test_11_reduce_signal_produces_negative_adaptation_direction(self):
        """11. Reduce signal produces a negative adaptation target on the targeted feature."""
        signal = CanonicalLearningSignal(
            target_feature="bmi",
            direction="reduce",
            scope="feature_specific",
        )
        x_row, target = _build_training_row(
            screening_record=self.screening,
            structured_category="bmi_overweighted",
            canonical_signal=signal,
        )
        self.assertEqual(target, -1.0)
        bmi_idx = ADAPTATION_FEATURE_NAMES.index("bmi")
        self.assertGreater(x_row[bmi_idx], 0.0)

    def test_12_increase_signal_produces_positive_adaptation_direction(self):
        """12. Increase signal produces a positive adaptation target on the targeted feature."""
        signal = CanonicalLearningSignal(
            target_feature="bmi",
            direction="increase",
            scope="feature_specific",
        )
        x_row, target = _build_training_row(
            screening_record=self.screening,
            structured_category="bmi_underweighted",
            canonical_signal=signal,
        )
        self.assertEqual(target, 1.0)
        bmi_idx = ADAPTATION_FEATURE_NAMES.index("bmi")
        self.assertGreater(x_row[bmi_idx], 0.0)

    def test_13_no_learning_signal_produces_zero_adaptation(self):
        """13. No-learning signal produces zero adaptation target and zero row vector."""
        signal = NULL_SIGNAL
        x_row, target = _build_training_row(
            screening_record=self.screening,
            structured_category="no_learning_signal",
            canonical_signal=signal,
        )
        self.assertEqual(target, 0.0)
        self.assertEqual(float(x_row.sum()), 0.0)

    def test_14_feature_specific_signal_does_not_target_unrelated_features(self):
        """14. Feature-specific signal attributes non-zero weight solely to the targeted feature."""
        signal = CanonicalLearningSignal(
            target_feature="bmi",
            direction="reduce",
            scope="feature_specific",
        )
        x_row, target = _build_training_row(
            screening_record=self.screening,
            structured_category="bmi_overweighted",
            canonical_signal=signal,
        )
        bmi_idx = ADAPTATION_FEATURE_NAMES.index("bmi")
        for i, name in enumerate(ADAPTATION_FEATURE_NAMES):
            if i == bmi_idx:
                self.assertGreater(x_row[i], 0.0)
            else:
                self.assertEqual(x_row[i], 0.0, f"Unrelated feature '{name}' was unexpectedly targeted")


class BackwardCompatibilityTests(TestCase):
    """Part 7D: Backward Compatibility (Tests 15-17)."""

    def test_15_existing_case_a_historical_record_remains_readable(self):
        """15. Historical feedback records without direction-aware fields remain readable."""
        rec = ScreeningRecord.objects.create(
            age=55,
            sex='male',
            bmi=Decimal('32.1'),
            waist_cm=Decimal('105.0'),
            hypertension_history='yes',
            smoking_history='yes',
            sedentary_minutes_day=600,
            screening_probability=0.341141,
            ai_referral_recommended=True,
            model_name="GAM",
            model_sha256="test",
            preprocessor_sha256="test",
        )
        rev = HumanReview.objects.create(
            screening_record=rec,
            review_action='overridden',
            final_referral_recommended=False,
            reviewer_code="RESEARCHER_HISTORICAL",
            override_reason_code="bmi_overweighted",
        )
        # Emulate historical v1.0 record where target_feature, direction, scope are NULL
        fb = HumanFeedback.objects.create(
            human_review=rev,
            structured_category="bmi_overweighted",
            relevant_feature="bmi",
            feedback_direction=DIR_REDUCE_INFLUENCE,
            target_feature=None,
            direction=None,
            scope=None,
            is_eligible_for_learning=True,
            learning_status='pending',
            model_version_at_feedback="GAM-v1-baseline",
            taxonomy_version="1.0",
        )

        fb.refresh_from_db()
        self.assertEqual(fb.structured_category, "bmi_overweighted")
        self.assertIsNone(fb.target_feature)

        # Canonical parser resolves historical record cleanly
        canonical = parse_canonical_signal(category_id=fb.structured_category)
        self.assertEqual(canonical.target_feature, "bmi")
        self.assertEqual(canonical.direction, "reduce")
        self.assertEqual(canonical.scope, "feature_specific")

    def test_16_historical_case_a_to_b_experiment_reproducible(self):
        """16. Existing Case A -> Case B experiment remains reproducible with exact outputs."""
        exp, case_a_rec = start_controlled_experiment()
        self.assertAlmostEqual(case_a_rec.screening_probability, 0.341141, places=4)
        self.assertTrue(case_a_rec.ai_referral_recommended)

        review, feedback = record_review_with_learning_signal(
            screening_record=case_a_rec,
            reviewer_code="EXP-R001",
            human_decision="override",
            override_factor="bmi_overweighted",
            rationale="BMI appears over-weighted for Case A.",
        )
        self.assertIsNotNone(review)
        self.assertFalse(review.final_referral_recommended)

        learn_res = run_controlled_learning(str(exp.id))
        self.assertTrue(learn_res['success'], msg=learn_res.get('error'))

        act_res = activate_controlled_adaptation(str(exp.id))
        self.assertTrue(act_res['success'], msg=act_res.get('error'))

        eval_res = evaluate_controlled_case_b(str(exp.id))
        self.assertTrue(eval_res['success'], msg=eval_res.get('error'))

        exp.refresh_from_db()
        self.assertAlmostEqual(exp.case_b_similarity, 0.9846, places=3)
        self.assertAlmostEqual(exp.case_b_baseline_probability, 0.311198, places=4)
        self.assertAlmostEqual(exp.case_b_adapted_probability, 0.270487, places=4)
        self.assertAlmostEqual(exp.case_b_probability_delta, -0.040711, places=4)

    def test_17_historical_raw_feedback_values_preserved(self):
        """17. Raw feedback strings (e.g. 'bmi_overweighted') are never rewritten in the database."""
        rec = ScreeningRecord.objects.create(
            age=45, sex='female', bmi=Decimal('29.0'), waist_cm=Decimal('90.0'),
            hypertension_history='no', smoking_history='no', sedentary_minutes_day=400,
            screening_probability=0.20, ai_referral_recommended=True,
            model_name="GAM", model_sha256="test", preprocessor_sha256="test",
        )
        rev = HumanReview.objects.create(
            screening_record=rec, review_action='overridden',
            final_referral_recommended=False, reviewer_code="AUDITOR_01",
            override_reason_code="bmi_overweighted",
        )
        fb = HumanFeedback.objects.create(
            human_review=rev,
            structured_category="bmi_overweighted",
            relevant_feature="bmi",
            feedback_direction=DIR_REDUCE_INFLUENCE,
            target_feature="bmi",
            direction="reduce",
            scope="feature_specific",
            is_eligible_for_learning=True,
            taxonomy_version=TAXONOMY_VERSION,
        )
        fb.refresh_from_db()
        self.assertEqual(fb.structured_category, "bmi_overweighted")
        self.assertEqual(fb.relevant_feature, "bmi")


class SafetyAndIsolationTests(TestCase):
    """Part 7E: Safety & Research Governance Isolation (Tests 18-22)."""

    def test_18_evaluation_participant_feedback_cannot_enter_learning_batch(self):
        """18. Evaluation participant feedback is strictly excluded from learning batches."""
        original_mode = getattr(settings, 'APP_MODE', 'feedback_lab')
        try:
            settings.APP_MODE = 'evaluation'
            rec = ScreeningRecord.objects.create(
                age=50, sex='male', bmi=Decimal('30.0'), waist_cm=Decimal('98.0'),
                hypertension_history='yes', smoking_history='no', sedentary_minutes_day=450,
                screening_probability=0.25, ai_referral_recommended=True,
                model_name="GAM", model_sha256="test", preprocessor_sha256="test",
            )
            ScreeningExplanation.objects.create(
                screening_record=rec, status='generated', intercept=-2.0,
                reconstructed_linear_predictor=-1.1, reconstructed_probability=0.25,
                contributions_json=[], reconstruction_error=0.0001, model_sha256="test",
            )
            review, fb = record_review_with_learning_signal(
                screening_record=rec,
                reviewer_code="PARTICIPANT_ISOLATION_TEST",
                human_decision="override",
                override_factor="bmi_overweighted",
                rationale="Should never enter learning batch",
            )
            self.assertFalse(fb.is_eligible_for_learning)
            self.assertEqual(fb.learning_status, "excluded")

            # collect_eligible_feedback must NOT include this record
            eligible = collect_eligible_feedback()
            self.assertNotIn(fb, eligible)
        finally:
            settings.APP_MODE = original_mode

    def test_19_feedback_lab_can_execute_controlled_learning(self):
        """19. Feedback Lab can execute controlled learning updates using eligible feedback."""
        original_mode = getattr(settings, 'APP_MODE', 'feedback_lab')
        try:
            settings.APP_MODE = 'feedback_lab'
            rec = ScreeningRecord.objects.create(
                age=52, sex='male', bmi=Decimal('31.0'), waist_cm=Decimal('99.0'),
                hypertension_history='yes', smoking_history='no', sedentary_minutes_day=480,
                screening_probability=0.28, ai_referral_recommended=True,
                model_name="GAM", model_sha256="test", preprocessor_sha256="test",
            )
            ScreeningExplanation.objects.create(
                screening_record=rec, status='generated', intercept=-2.0,
                reconstructed_linear_predictor=-1.0, reconstructed_probability=0.28,
                contributions_json=[], reconstruction_error=0.0001, model_sha256="test",
            )
            review, fb = record_review_with_learning_signal(
                screening_record=rec,
                reviewer_code="LAB_RESEARCHER",
                human_decision="override",
                override_factor="bmi_overweighted",
                rationale="Controlled feedback lab test",
                target_feature="bmi",
                signal_direction="reduce",
                signal_scope="feature_specific",
            )
            self.assertTrue(fb.is_eligible_for_learning)
            self.assertEqual(fb.learning_status, "pending")
            self.assertEqual(fb.target_feature, "bmi")
            self.assertEqual(fb.direction, "reduce")

            training_result = train_adaptation_layer([fb], min_feedback=1)
            self.assertTrue(training_result.success)
            self.assertGreater(len(training_result.artifact_sha256), 0)
        finally:
            settings.APP_MODE = original_mode

    def test_20_frozen_gam_artifact_hash_unchanged(self):
        """20. Frozen GAM-v1 SHA-256 matches exactly the locked thesis specification."""
        paths = get_artifact_paths()
        gam_path = Path(paths["gam"])
        self.assertTrue(gam_path.exists(), f"GAM artifact missing at {gam_path}")
        with open(gam_path, 'rb') as f:
            computed_sha = hashlib.sha256(f.read()).hexdigest()
        self.assertEqual(
            computed_sha,
            EXPECTED_GAM_SHA256,
            "CRITICAL: Frozen GAM-v1 artifact SHA-256 hash has been altered!"
        )

    def test_21_decision_threshold_remains_exactly_0_1389(self):
        """21. Decision threshold is locked at exactly 0.1389."""
        self.assertEqual(
            Decimal(str(FROZEN_DECISION_THRESHOLD)),
            Decimal('0.1389'),
            "CRITICAL: Frozen decision threshold has been altered!"
        )
        self.assertEqual(float(FROZEN_DECISION_THRESHOLD), 0.1389)

    def test_22_final_test_artifacts_untouched(self):
        """22. Final test artifacts (N=812) exist and remain untouched."""
        project_root = Path(settings.BASE_DIR).parent
        pred_path = project_root / "nhanes_feasibility_2021_2023" / "predictions_phase5" / "final_test_predictions.csv"
        parquet_path = project_root / "nhanes_feasibility_2021_2023" / "processed_phase3" / "analytic_expanded_complete.parquet"

        self.assertTrue(pred_path.exists(), f"Final test predictions missing: {pred_path}")
        self.assertTrue(parquet_path.exists(), f"Analytic dataset missing: {parquet_path}")

        # Verify N=812 observations in final test predictions
        import pandas as pd
        df = pd.read_csv(pred_path)
        self.assertEqual(len(df), 812, f"Expected 812 final-test rows, found {len(df)}")

    def test_23_evaluation_mode_footer_renders_frozen_model_notice(self):
        """23. Evaluation Mode footer renders frozen-model notice and not live-learning notice."""
        original_mode = getattr(settings, 'APP_MODE', 'feedback_lab')
        try:
            rec = ScreeningRecord.objects.create(
                age=50, sex='female', bmi=Decimal('28.5'), waist_cm=Decimal('90.0'),
                hypertension_history='no', smoking_history='no', sedentary_minutes_day=300,
                screening_probability=0.20, ai_referral_recommended=True,
                model_name="GAM", model_sha256="test", preprocessor_sha256="test",
            )
            ScreeningExplanation.objects.create(
                screening_record=rec, status='generated', intercept=-2.0,
                reconstructed_linear_predictor=-1.0, reconstructed_probability=0.20,
                contributions_json=[], reconstruction_error=0.0001, model_sha256="test",
            )
            url = reverse('predictor:screening_result', kwargs={'screening_id': rec.id})

            # In Evaluation Mode
            settings.APP_MODE = 'evaluation'
            response_eval = self.client.get(url)
            self.assertEqual(response_eval.status_code, 200)
            content_eval = response_eval.content.decode('utf-8')

            expected_eval_notice = (
                "Evaluation Mode uses a frozen model. Human overrides are recorded for research analysis only and do not trigger model adaptation."
            )
            contradictory_notice = (
                "Human overrides generate the learning signal directly within this unified review action."
            )

            self.assertIn(expected_eval_notice, content_eval)
            self.assertNotIn(contradictory_notice, content_eval)

            # In Feedback Lab Mode
            settings.APP_MODE = 'feedback_lab'
            response_fl = self.client.get(url)
            self.assertEqual(response_fl.status_code, 200)
            content_fl = response_fl.content.decode('utf-8')

            self.assertIn(contradictory_notice, content_fl)
            self.assertNotIn(expected_eval_notice, content_fl)
        finally:
            settings.APP_MODE = original_mode

    def test_24_feedback_lab_no_learning_signal_disallows_directional_combination(self):
        """24. No learning signal in Feedback Lab cannot be combined with directional adjustments."""
        from predictor.forms import UnifiedHumanReviewForm

        # 1. Target feature 'none' with 'reduce' or 'increase' must be rejected
        form_reduce = UnifiedHumanReviewForm(data={
            'reviewer_code': 'LAB_USER',
            'human_decision': 'override',
            'override_factor': 'no_learning_signal',
            'target_feature': 'none',
            'signal_direction': 'reduce',
            'signal_scope': 'feature_specific',
            'rationale': 'Disagreement without learning',
        })
        self.assertFalse(form_reduce.is_valid())
        self.assertIn('signal_direction', form_reduce.errors)
        self.assertIn(
            'No learning signal cannot be combined with directional adjustments',
            str(form_reduce.errors['signal_direction'])
        )

        form_increase = UnifiedHumanReviewForm(data={
            'reviewer_code': 'LAB_USER',
            'human_decision': 'override',
            'override_factor': 'no_learning_signal',
            'target_feature': 'none',
            'signal_direction': 'increase',
            'signal_scope': 'feature_specific',
            'rationale': 'Disagreement without learning',
        })
        self.assertFalse(form_increase.is_valid())
        self.assertIn('signal_direction', form_increase.errors)

        # 2. Target feature 'none' with direction 'none' (or empty) must be valid and normalized
        form_valid = UnifiedHumanReviewForm(data={
            'reviewer_code': 'LAB_USER',
            'human_decision': 'override',
            'override_factor': 'no_learning_signal',
            'target_feature': 'none',
            'signal_direction': 'none',
            'signal_scope': 'none',
            'rationale': 'Purely qualitative override',
        })
        self.assertTrue(form_valid.is_valid())
        self.assertEqual(form_valid.cleaned_data['target_feature'], 'none')
        self.assertEqual(form_valid.cleaned_data['signal_direction'], 'none')
        self.assertEqual(form_valid.cleaned_data['signal_scope'], 'none')

        # 3. parse_canonical_signal rejects inconsistent none + directional combinations
        parsed = parse_canonical_signal(target_feature='none', direction='reduce', scope='feature_specific')
        self.assertEqual(parsed, NULL_SIGNAL)
        self.assertEqual(parsed.direction, 'none')
        self.assertEqual(parsed.target_feature, 'none')

        # 4. Feedback Lab UI verifies data-target="none" and direction clearing logic
        original_mode = getattr(settings, 'APP_MODE', 'feedback_lab')
        try:
            rec = ScreeningRecord.objects.create(
                age=50, sex='female', bmi=Decimal('28.5'), waist_cm=Decimal('90.0'),
                hypertension_history='no', smoking_history='no', sedentary_minutes_day=300,
                screening_probability=0.20, ai_referral_recommended=True,
                model_name="GAM", model_sha256="test", preprocessor_sha256="test",
            )
            ScreeningExplanation.objects.create(
                screening_record=rec, status='generated', intercept=-2.0,
                reconstructed_linear_predictor=-1.0, reconstructed_probability=0.20,
                contributions_json=[], reconstruction_error=0.0001, model_sha256="test",
            )
            settings.APP_MODE = 'feedback_lab'
            url = reverse('predictor:screening_result', kwargs={'screening_id': rec.id})
            response = self.client.get(url)
            content = response.content.decode('utf-8')
            self.assertIn('data-target="none"', content)
            self.assertIn("signal-direction-none", content)
            self.assertIn("dirContainer.style.display = 'none'", content)
        finally:
            settings.APP_MODE = original_mode
