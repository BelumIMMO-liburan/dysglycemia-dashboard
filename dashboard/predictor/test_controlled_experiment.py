"""
Automated Test Suite for Primary Controlled Feedback Experiment (Thesis Gap #2).

Verifies the complete 11-step mechanism demonstration:
  Case A -> Frozen GAM -> Native XAI -> Real Human Review -> Human Override
  -> Override Factor -> Learning Signal -> Residual Adaptation
  -> 13/13 Technical Validation -> Active Adaptation -> Case B
  -> Baseline vs Adapted Output Comparison.

EPISTEMIC & GOVERNANCE BOUNDARIES:
1. Small-N Controlled Mechanism Demonstration: proves feedback can alter similar-case output.
2. No claim of generalized model retraining or clinical accuracy improvement.
3. Frozen Phase-5 GAM (λ=10.0, Splines=10, Threshold=0.1389) is strictly immutable.
4. Case B inference uses ONLY Case B's own 7 predictors and the active adaptation artifact;
   Case B NEVER receives Case A metadata.
5. Evaluation Mode data and participants are strictly excluded.
"""

import math
from pathlib import Path
from django.test import TestCase, Client
from django.urls import reverse
from django.conf import settings

from predictor.models import (
    ScreeningRecord,
    ScreeningExplanation,
    HumanReview,
    HumanFeedback,
    ModelVersion,
    FeedbackLearningBatch,
    SimilarCaseComparison,
    ControlledFeedbackExperiment,
)
from predictor.services.screening_inference import (
    predict_screening,
    EXPECTED_GAM_SHA256,
    FROZEN_DECISION_THRESHOLD,
    get_artifact_paths,
)
from predictor.services.screening_explanation import explain_screening
from predictor.services.adapted_inference import predict_adapted
from predictor.services.similarity import compute_similarity
from predictor.services.feedback_learning import (
    CONTROLLED_CASE_A_DATA,
    CONTROLLED_CASE_B_DATA,
    start_controlled_experiment,
    run_controlled_learning,
    activate_controlled_adaptation,
    evaluate_controlled_case_b,
    record_review_with_learning_signal,
    execute_learning_batch,
    get_active_controlled_experiment,
    get_latest_controlled_experiment,
)
from predictor.services.model_versioning import (
    ensure_baseline_version,
    get_active_version,
    get_baseline_version,
    get_model_status_summary,
    BASELINE_VERSION_LABEL,
    _compute_file_sha256,
)


class ControlledFeedbackExperimentTests(TestCase):
    """Rigorous end-to-end verification of the controlled mechanism demonstration."""

    def setUp(self):
        self.client = Client()
        ensure_baseline_version()

    def test_case_a_baseline_prediction_exact_targets(self):
        """Case A under frozen GAM must yield probability ~0.341141 and REFER."""
        result = predict_screening(CONTROLLED_CASE_A_DATA)
        self.assertAlmostEqual(result.probability, 0.341141, places=4)
        self.assertTrue(result.referral_recommended)
        self.assertEqual(FROZEN_DECISION_THRESHOLD, 0.1389)

    def test_case_b_baseline_prediction_exact_targets(self):
        """Case B under frozen GAM must yield probability ~0.311198 and REFER."""
        result = predict_screening(CONTROLLED_CASE_B_DATA)
        self.assertAlmostEqual(result.probability, 0.311198, places=4)
        self.assertTrue(result.referral_recommended)

    def test_case_a_and_case_b_similarity_score(self):
        """Case A and Case B must satisfy similarity >= 0.85 (expected ~0.9846)."""
        sim = compute_similarity(CONTROLLED_CASE_A_DATA, CONTROLLED_CASE_B_DATA)
        self.assertAlmostEqual(sim.similarity_score, 0.9846, places=3)
        self.assertTrue(sim.is_similar)

    def test_end_to_end_controlled_mechanism_demonstration(self):
        """
        Execute full controlled experiment state machine:
        READY -> CASE_A_CREATED -> HUMAN_REVIEW_PENDING -> OVERRIDE_RECORDED
        -> LEARNING_SIGNAL_CREATED -> CANDIDATE_CREATED -> VALIDATION_PASSED
        -> ADAPTATION_ACTIVE -> CASE_B_CREATED -> CASE_B_EVALUATED -> COMPARISON_COMPLETE
        """
        # --- Step 1: Start Controlled Experiment ---
        exp, case_a_rec = start_controlled_experiment()
        self.assertIsNotNone(exp)
        self.assertEqual(exp.state, 'HUMAN_REVIEW_PENDING')
        self.assertEqual(exp.case_a.id, case_a_rec.id)
        self.assertAlmostEqual(case_a_rec.screening_probability, 0.341141, places=4)
        self.assertTrue(case_a_rec.ai_referral_recommended)

        # --- Step 2: Real Human Review & Override on Case A ---
        # Note: In the web UI, this is performed by the human reviewer submitting the form.
        # Here we invoke record_review_with_learning_signal as the service boundary.
        review, feedback = record_review_with_learning_signal(
            screening_record=case_a_rec,
            reviewer_code="EXP-R001",
            human_decision="override",
            override_factor="bmi_overweighted",
            rationale="BMI appears to have contributed too strongly to the screening assessment for this case and should be moderated for similar cases.",
        )
        self.assertIsNotNone(review)
        self.assertEqual(review.review_action, 'overridden')
        self.assertFalse(review.final_referral_recommended)
        self.assertIsNotNone(feedback)
        self.assertTrue(feedback.is_eligible_for_learning)
        self.assertEqual(feedback.learning_status, 'pending')
        self.assertEqual(feedback.structured_category, 'bmi_overweighted')

        # Verify state machine progressed via hook
        exp.refresh_from_db()
        self.assertEqual(exp.state, 'LEARNING_SIGNAL_CREATED')
        self.assertEqual(exp.override_factor, 'bmi_overweighted')
        self.assertEqual(exp.learning_signal.id, feedback.id)

        # --- Step 3: Run Controlled Learning ---
        learn_res = run_controlled_learning(str(exp.id))
        self.assertTrue(learn_res['success'], msg=learn_res.get('error'))

        exp.refresh_from_db()
        self.assertEqual(exp.state, 'VALIDATION_PASSED')
        self.assertIsNotNone(exp.candidate_adaptation)
        self.assertTrue(exp.candidate_adaptation.version_label.startswith('RA-v'))
        self.assertEqual(exp.candidate_adaptation.validation_status, 'passed')

        # Verify 13/13 technical validation checks passed
        metrics = exp.candidate_adaptation.validation_metrics
        self.assertIsNotNone(metrics)
        checks = metrics.get('checks', [])
        self.assertEqual(len(checks), 13)
        for chk in checks:
            self.assertTrue(chk['passed'], f"Check '{chk['check']}' failed: {chk}")

        # --- Step 4: Activate Adaptation ---
        act_res = activate_controlled_adaptation(str(exp.id))
        self.assertTrue(act_res['success'], msg=act_res.get('error'))

        exp.refresh_from_db()
        self.assertEqual(exp.state, 'ADAPTATION_ACTIVE')
        self.assertIsNotNone(exp.active_adaptation)
        self.assertTrue(exp.active_adaptation.is_active)

        # Verify terminology helper
        status = get_model_status_summary()
        self.assertEqual(status['baseline_model'], "GAM-v1 · Frozen")
        self.assertIn("Validated & Active", status['active_adaptation'])

        # --- Step 5: Evaluate Case B (Subsequent Similar Case) ---
        eval_res = evaluate_controlled_case_b(str(exp.id))
        self.assertTrue(eval_res['success'], msg=eval_res.get('error'))

        exp.refresh_from_db()
        self.assertEqual(exp.state, 'COMPARISON_COMPLETE')
        self.assertIsNotNone(exp.case_b)

        # Verify mathematical targets for Case B
        self.assertAlmostEqual(exp.case_b_similarity, 0.9846, places=3)
        self.assertAlmostEqual(exp.case_b_baseline_probability, 0.311198, places=4)
        self.assertAlmostEqual(exp.case_b_adapted_probability, 0.270487, places=4)
        self.assertAlmostEqual(exp.case_b_probability_delta, -0.040711, places=4)
        self.assertAlmostEqual(exp.case_b_log_odds_delta, -0.1980, places=2)

        # Verify Complete Data Provenance
        self.assertIsNotNone(exp.id)
        self.assertIsNotNone(exp.case_a_id)
        self.assertIsNotNone(exp.human_review_id)
        self.assertEqual(exp.override_factor, 'bmi_overweighted')
        self.assertIsNotNone(exp.learning_signal_id)
        self.assertIsNotNone(exp.learning_batch_id)
        self.assertIsNotNone(exp.candidate_adaptation_id)
        self.assertIsNotNone(exp.validation_id)
        self.assertIsNotNone(exp.active_adaptation_id)
        self.assertIsNotNone(exp.case_b_id)

        # Verify SimilarCaseComparison was created
        comp = SimilarCaseComparison.objects.filter(source_case=exp.case_a, target_case=exp.case_b).first()
        self.assertIsNotNone(comp)
        self.assertAlmostEqual(comp.baseline_probability, 0.311198, places=4)
        self.assertAlmostEqual(comp.updated_probability, 0.270487, places=4)
        self.assertAlmostEqual(comp.probability_delta, -0.040711, places=4)

        # --- Step 6: Verify Case B Did NOT Use Case A Metadata ---
        # Direct inference on Case B with the active adaptation must match the stored result exactly.
        direct_b = predict_adapted(CONTROLLED_CASE_B_DATA)
        self.assertAlmostEqual(direct_b.adapted_probability, exp.case_b_adapted_probability, places=6)
        self.assertAlmostEqual(direct_b.delta_log_odds, exp.case_b_log_odds_delta, places=4)

        # --- Step 7: Verify Frozen GAM Integrity ---
        gam_path = get_artifact_paths()["gam"]
        current_sha = _compute_file_sha256(str(gam_path))
        self.assertEqual(current_sha, EXPECTED_GAM_SHA256)

    def test_case_b_evaluation_guardrail_requires_active_adaptation(self):
        """Case B evaluation must strictly fail if adaptation is not active."""
        exp, case_a = start_controlled_experiment()
        res = evaluate_controlled_case_b(str(exp.id))
        self.assertFalse(res['success'])
        self.assertIn("Expected 'ADAPTATION_ACTIVE'", res['error'])

    def test_evaluation_mode_data_isolation(self):
        """Records from evaluation mode or practice cases cannot enter controlled learning."""
        case_a_eval = ScreeningRecord.objects.create(
            age=55,
            sex="Male",
            bmi=32.1,
            waist_cm=105.0,
            hypertension_history="Yes",
            smoking_history="Yes",
            sedentary_minutes_day=600,
            screening_probability=0.341141,
            ai_referral_recommended=True,
            is_practice=True,  # Practice record
        )
        ScreeningExplanation.objects.create(
            screening_record=case_a_eval,
            method="gam_native_additive",
            intercept=-2.365,
            contributions_json=[],
            reconstructed_linear_predictor=-1.077,
            reconstructed_probability=0.254,
            reconstruction_error=0.0001,
            status='generated',
        )

        review, feedback = record_review_with_learning_signal(
            screening_record=case_a_eval,
            reviewer_code="PRACTICE-USER",
            human_decision="override",
            override_factor="bmi_overweighted",
            rationale="Practice test",
        )
        self.assertIsNotNone(feedback)
        self.assertFalse(feedback.is_eligible_for_learning)
        self.assertEqual(feedback.learning_status, 'excluded')

    def test_accepting_ai_does_not_create_corrective_learning_signal(self):
        """Accepting AI referral creates no corrective learning signal."""
        case_rec = ScreeningRecord.objects.create(
            age=55,
            sex="Male",
            bmi=32.1,
            waist_cm=105.0,
            hypertension_history="Yes",
            smoking_history="Yes",
            sedentary_minutes_day=600,
            screening_probability=0.341141,
            ai_referral_recommended=True,
            is_practice=False,
        )
        ScreeningExplanation.objects.create(
            screening_record=case_rec,
            method="gam_native_additive",
            intercept=-2.365,
            contributions_json=[],
            reconstructed_linear_predictor=-1.077,
            reconstructed_probability=0.254,
            reconstruction_error=0.0001,
            status='generated',
        )

        review, feedback = record_review_with_learning_signal(
            screening_record=case_rec,
            reviewer_code="R001",
            human_decision="accept",
            override_factor=None,
            rationale="Concordant review.",
        )
        self.assertEqual(review.review_action, 'accepted')
        if feedback:
            self.assertFalse(feedback.is_eligible_for_learning)
            self.assertEqual(feedback.learning_status, 'excluded')

    def test_secondary_accumulated_batch_learning_requires_min_3(self):
        """Accumulated batch learning preserves the secondary min_feedback=3 requirement."""
        res = execute_learning_batch(min_feedback=3)
        # Should report insufficient feedback if fewer than 3 pending records
        self.assertFalse(res['success'])
        self.assertIn("minimum", res['error'])
