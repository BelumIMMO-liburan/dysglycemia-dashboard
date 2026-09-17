"""
Comprehensive automated test suite for Evaluation Mode and Dual-Mode Isolation.
Protocol E1 v1.0.3 & E2 Implementation.

Tests:
1. Backend Route Isolation:
   - Evaluates @require_app_mode('feedback_lab') returning HTTP 403 Forbidden when APP_MODE == 'evaluation'.
   - Verifies researcher access is granted when APP_MODE == 'feedback_lab'.
2. Evaluation Participant Workflow:
   - Informed consent & demographic intake.
   - Practice Case P0 onboarding & is_practice isolation.
   - Feedback exclusion in evaluation mode.
   - 4-part Evaluation Questionnaire scoring and persistence.
   - Completion confirmation concealing test scores.
3. Scoring Engines:
   - Server-side Comprehension scoring (8 items, 0–8, %).
   - Standard Indonesian SUS scoring (10 items, 0.0–100.0).
"""

from decimal import Decimal
import uuid
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from predictor.models import (
    ScreeningRecord,
    ScreeningExplanation,
    HumanReview,
    HumanFeedback,
    ModelVersion,
    EvaluationRespondent,
    EvaluationSession,
    EvaluationEvent,
    QuestionnaireResponse,
)
from predictor.services.questionnaire import (
    score_comprehension,
    score_sus,
    COMPREHENSION_ANSWER_KEYS,
    PRACTICE_CASE_P0,
)


class DualModeRouteProtectionTests(TestCase):
    """Verifies that researcher endpoints are strictly blocked in evaluation mode."""

    def setUp(self):
        # Create a sample screening record
        self.record = ScreeningRecord.objects.create(
            age=55,
            sex='male',
            bmi=28.5,
            waist_cm=95.0,
            hypertension_history='yes',
            smoking_history='no',
            sedentary_minutes_day=420,
            screening_probability=0.35,
            ai_referral_recommended=True,
            decision_threshold=Decimal('0.1389'),
            model_name='GAM',
            model_sha256='test_sha',
            preprocessor_sha256='test_prep_sha',
            input_schema_version='1.0',
        )

    @override_settings(APP_MODE='evaluation')
    def test_feedback_experiment_blocked_in_evaluation_mode(self):
        """GET /feedback-experiment/ must return 403 Forbidden in evaluation mode."""
        url = reverse('predictor:feedback_experiment')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)
        self.assertIn("Access Denied", response.content.decode())

    @override_settings(APP_MODE='evaluation')
    def test_trigger_learning_blocked_in_evaluation_mode(self):
        """POST /feedback-experiment/trigger-learning/ must return 403 in evaluation mode."""
        url = reverse('predictor:trigger_learning')
        response = self.client.post(url)
        self.assertEqual(response.status_code, 403)

    @override_settings(APP_MODE='evaluation')
    def test_activate_candidate_blocked_in_evaluation_mode(self):
        """POST /feedback-experiment/activate-candidate/ must return 403 in evaluation mode."""
        url = reverse('predictor:activate_candidate')
        response = self.client.post(url, {'batch_id': str(uuid.uuid4())})
        self.assertEqual(response.status_code, 403)

    @override_settings(APP_MODE='evaluation')
    def test_rollback_version_blocked_in_evaluation_mode(self):
        """POST /feedback-experiment/rollback/ must return 403 in evaluation mode."""
        url = reverse('predictor:rollback_version')
        response = self.client.post(url)
        self.assertEqual(response.status_code, 403)

    @override_settings(APP_MODE='evaluation')
    def test_run_comparison_blocked_in_evaluation_mode(self):
        """POST /screening/<id>/compare/ must return 403 in evaluation mode."""
        url = reverse('predictor:run_comparison', kwargs={'screening_id': self.record.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 403)

    @override_settings(APP_MODE='feedback_lab')
    def test_feedback_experiment_allowed_in_feedback_lab_mode(self):
        """GET /feedback-experiment/ must return 200 OK in feedback_lab mode."""
        url = reverse('predictor:feedback_experiment')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)


class ScoringEngineUnitTests(TestCase):
    """Tests objective comprehension and SUS scoring algorithms."""

    def test_comprehension_all_correct(self):
        """All correct answers must yield 8/8 (100.0%)."""
        answers = dict(COMPREHENSION_ANSWER_KEYS)
        score, pct = score_comprehension(answers)
        self.assertEqual(score, 8)
        self.assertEqual(pct, 100.0)

    def test_comprehension_all_wrong(self):
        """All incorrect answers must yield 0/8 (0.0%)."""
        answers = {k: 'Z' for k in COMPREHENSION_ANSWER_KEYS}
        score, pct = score_comprehension(answers)
        self.assertEqual(score, 0)
        self.assertEqual(pct, 0.0)

    def test_comprehension_half_correct(self):
        """4 correct answers must yield 4/8 (50.0%)."""
        answers = {}
        for i, (k, v) in enumerate(COMPREHENSION_ANSWER_KEYS.items()):
            answers[k] = v if i < 4 else 'Z'
        score, pct = score_comprehension(answers)
        self.assertEqual(score, 4)
        self.assertEqual(pct, 50.0)

    def test_sus_all_maximum(self):
        """All 5s must yield 100.0 SUS score."""
        responses = {k: 5 for k in range(1, 11)}
        # Odd: 5-1 = 4. Even: 5-5 = 0. Sum = 5*4 + 5*0 = 20. Total = 20 * 2.5 = 50.0.
        # Wait, if even items are negative polarity, answering 5 (Strongly Agree) to negative items reduces score!
        # Answering 5 to positive items and 1 to negative items gives 100.0!
        ideal_responses = {
            1: 5, 2: 1, 3: 5, 4: 1, 5: 5,
            6: 1, 7: 5, 8: 1, 9: 5, 10: 1
        }
        score = score_sus(ideal_responses)
        self.assertEqual(score, 100.0)

    def test_sus_all_minimum(self):
        """Worst possible responses: 1 to positive items, 5 to negative items."""
        worst_responses = {
            1: 1, 2: 5, 3: 1, 4: 5, 5: 1,
            6: 5, 7: 1, 8: 5, 9: 1, 10: 5
        }
        score = score_sus(worst_responses)
        self.assertEqual(score, 0.0)

    def test_sus_all_neutral(self):
        """All 3s (Neutral) must yield 50.0 SUS score."""
        neutral_responses = {k: 3 for k in range(1, 11)}
        score = score_sus(neutral_responses)
        self.assertEqual(score, 50.0)

    def test_sus_validation_rejects_invalid_count(self):
        """score_sus requires exactly 10 responses."""
        with self.assertRaises(ValueError):
            score_sus({1: 3, 2: 3})


class EvaluationParticipantWorkflowTests(TestCase):
    """End-to-end integration tests for participant evaluation mode."""

    @override_settings(APP_MODE='evaluation')
    def test_complete_evaluation_participant_flow(self):
        """
        Tests the full sequence:
        1. Informed Consent & Demographic intake
        2. Practice Case P0 walkthrough
        3. Screening intake
        4. Human Review & Feedback (verified excluded from learning)
        5. 4-part Questionnaire submission & server-side scoring
        6. Completion confirmation page
        """
        # Step 1: Consent Form GET & POST
        consent_url = reverse('predictor:evaluation_consent')
        get_res = self.client.get(consent_url)
        self.assertEqual(get_res.status_code, 200)
        self.assertContains(get_res, "Persetujuan Partisipasi Penelitian")

        post_data = {
            'age_group': '25-34',
            'education_level': 'sarjana',
            'technical_background': 'intermediate',
            'health_background': 'layperson',
            'consent_given': 'on',
        }
        consent_res = self.client.post(consent_url, post_data)
        self.assertRedirects(consent_res, reverse('predictor:evaluation_practice'))

        # Verify respondent and session created
        self.assertEqual(EvaluationRespondent.objects.count(), 1)
        respondent = EvaluationRespondent.objects.first()
        self.assertTrue(respondent.respondent_code.startswith("R-"))
        self.assertEqual(respondent.age_group, '25-34')

        session = EvaluationSession.objects.first()
        self.assertEqual(session.status, 'in_progress')
        self.assertFalse(session.practice_completed)
        self.assertFalse(session.questionnaire_completed)

        # Step 2: Practice Case P0
        practice_url = reverse('predictor:evaluation_practice')
        p_res = self.client.get(practice_url)
        self.assertEqual(p_res.status_code, 200)
        self.assertContains(p_res, "Kasus Latihan P0")

        # Verify P0 screening record was created with is_practice=True
        p0_record = ScreeningRecord.objects.filter(is_practice=True).first()
        self.assertIsNotNone(p0_record)
        self.assertEqual(p0_record.age, PRACTICE_CASE_P0['features']['age'])

        # Finish practice
        p_finish_res = self.client.post(practice_url, {'action': 'finish_practice'})
        self.assertRedirects(p_finish_res, reverse('predictor:new_screening'))
        session.refresh_from_db()
        self.assertTrue(session.practice_completed)

        # Step 3: Run a screening case
        run_url = reverse('predictor:run_screening')
        screening_data = {
            'age': 50,
            'sex': 'female',
            'bmi': 29.0,
            'waist_cm': 92.0,
            'hypertension_history': 'yes',
            'smoking_history': 'no',
            'sedentary_minutes_day': 360,
        }
        run_res = self.client.post(run_url, screening_data)
        self.assertEqual(run_res.status_code, 302)
        screening_record = ScreeningRecord.objects.filter(is_practice=False).first()
        self.assertIsNotNone(screening_record)

        # Step 4: Override review & submit feedback
        override_url = reverse('predictor:override_review', kwargs={'screening_id': screening_record.id})
        override_res = self.client.post(override_url, {
            'reviewer_code': 'REV-TEST-01',
            'override_reason_code': 'additional_context_reduces_concern',
            'override_note': 'Participant evaluation test note',
        })
        self.assertEqual(override_res.status_code, 302)

        # Submit structured feedback
        feedback_url = reverse('predictor:submit_feedback', kwargs={'screening_id': screening_record.id})
        fb_res = self.client.post(feedback_url, {
            'structured_category': 'waist_overweighted',
            'feedback_text': 'Waist circumference is dominant here.',
        })
        self.assertEqual(fb_res.status_code, 302)

        # CRITICAL GOVERNANCE CHECK: Feedback in evaluation mode must NOT be eligible for learning
        feedback = HumanFeedback.objects.first()
        self.assertIsNotNone(feedback)
        self.assertFalse(feedback.is_eligible_for_learning)
        self.assertEqual(feedback.learning_status, 'excluded')

        # Step 5: Complete Questionnaire
        q_url = reverse('predictor:evaluation_questionnaire')
        q_get = self.client.get(q_url)
        self.assertEqual(q_get.status_code, 200)
        self.assertContains(q_get, "Bagian A: Pemahaman Konsep Dashboard")

        q_post_data = {
            # Section A (Comprehension): Let's provide all correct answers
            'c1': COMPREHENSION_ANSWER_KEYS['C1'],
            'c2': COMPREHENSION_ANSWER_KEYS['C2'],
            'c3': COMPREHENSION_ANSWER_KEYS['C3'],
            'c4': COMPREHENSION_ANSWER_KEYS['C4'],
            'c5': COMPREHENSION_ANSWER_KEYS['C5'],
            'c6': COMPREHENSION_ANSWER_KEYS['C6'],
            'c7': COMPREHENSION_ANSWER_KEYS['C7'],
            'c8': COMPREHENSION_ANSWER_KEYS['C8'],
            # Section B (SUS): All 4s (Good usability)
            'sus_1': 4, 'sus_2': 2, 'sus_3': 4, 'sus_4': 2, 'sus_5': 4,
            'sus_6': 2, 'sus_7': 4, 'sus_8': 2, 'sus_9': 4, 'sus_10': 2,
            # Section C (Clarity): All 5s
            'clarity_1': 5, 'clarity_2': 5, 'clarity_3': 5, 'clarity_4': 5, 'clarity_5': 5,
            # Section D (Open-ended)
            'open_1': 'Penjelasan visual XAI sangat membantu.',
            'open_2': 'Awalnya sedikit bingung dengan istilah disglikemia.',
            'open_3': 'Tingkatkan kontras warna pada mobile.',
        }
        q_post_res = self.client.post(q_url, q_post_data)
        self.assertRedirects(q_post_res, reverse('predictor:evaluation_complete'))

        # Verify QuestionnaireResponse persisted correctly
        self.assertEqual(QuestionnaireResponse.objects.count(), 1)
        q_resp = QuestionnaireResponse.objects.first()
        self.assertEqual(q_resp.comprehension_score, 8)
        self.assertEqual(q_resp.comprehension_pct, 100.0)
        self.assertEqual(q_resp.sus_score, 75.0)  # (3*5 + 3*5) * 2.5 = 30 * 2.5 = 75.0
        self.assertEqual(q_resp.clarity_1, 5)
        self.assertEqual(q_resp.open_1, 'Penjelasan visual XAI sangat membantu.')

        # Verify session completed
        session.refresh_from_db()
        self.assertTrue(session.questionnaire_completed)
        self.assertEqual(session.status, 'completed')
        self.assertIsNotNone(session.completed_at)

        # Step 6: Verify Completion page strictly conceals answer keys and scores
        complete_url = reverse('predictor:evaluation_complete')
        complete_res = self.client.get(complete_url)
        self.assertEqual(complete_res.status_code, 200)
        self.assertContains(complete_res, respondent.respondent_code)
        self.assertContains(complete_res, "Sesi Evaluasi Telah Selesai")
        # Ensure answer key or score is NOT displayed to participant
        self.assertNotContains(complete_res, "100.0%")
        self.assertNotContains(complete_res, "Kunci Jawaban")
