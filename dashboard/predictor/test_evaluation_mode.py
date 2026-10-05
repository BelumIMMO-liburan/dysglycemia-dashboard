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
from django.middleware.csrf import get_token
from django.test import TestCase, Client, RequestFactory, override_settings
from django.urls import reverse
from django.utils import timezone

from predictor.models import (
    ScreeningRecord,
    ScreeningExplanation,
    HumanReview,
    Stage2Assessment,
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

        # Finish practice -> Returns to normal dashboard overview
        p_finish_res = self.client.post(practice_url, {'action': 'finish_practice'})
        self.assertRedirects(p_finish_res, reverse('predictor:overview'))
        session.refresh_from_db()
        self.assertTrue(session.practice_completed)

        # Verify normal dashboard is accessible and displays standard navigation + additive research
        overview_res = self.client.get(reverse('predictor:overview'))
        self.assertEqual(overview_res.status_code, 200)
        self.assertContains(overview_res, "Screening Overview")
        self.assertContains(overview_res, "New Screening")
        self.assertContains(overview_res, "Review Queue")
        self.assertContains(overview_res, "History")
        self.assertContains(overview_res, "Analytics")
        self.assertContains(overview_res, "About the Model")
        self.assertContains(overview_res, "Research Evaluation")
        self.assertContains(overview_res, "Informed Consent")
        self.assertContains(overview_res, "Practice Case P0")
        self.assertContains(overview_res, "Questionnaire")

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


class DatabaseIsolationGuardTests(TestCase):
    """
    Automated verification of database isolation guards (Priority 3).
    Ensures that Feedback Lab cannot connect to Evaluation PostgreSQL DATABASE_URL,
    and that evaluation mode cannot accidentally fall back to development db.sqlite3.
    """

    def test_feedback_lab_with_database_url_raises_improperly_configured(self):
        """1. APP_MODE=feedback_lab + DATABASE_URL -> configuration failure."""
        import os, runpy
        from unittest import mock
        from django.core.exceptions import ImproperlyConfigured

        env = os.environ.copy()
        env['APP_MODE'] = 'feedback_lab'
        env['DATABASE_URL'] = 'postgresql://postgres:secret@roundhouse.proxy.rlwy.net:5432/railway'
        with mock.patch.dict(os.environ, env, clear=True):
            with self.assertRaises(ImproperlyConfigured) as ctx:
                runpy.run_module('dashboard.settings', run_name='__main__')
            self.assertIn("Feedback Lab requires local research storage", str(ctx.exception))

    def test_feedback_lab_without_database_url_uses_local_sqlite(self):
        """2. APP_MODE=feedback_lab without DATABASE_URL -> local Feedback Lab configuration works."""
        import os, runpy
        from unittest import mock

        env = os.environ.copy()
        env['APP_MODE'] = 'feedback_lab'
        env.pop('DATABASE_URL', None)
        with mock.patch.dict(os.environ, env, clear=True):
            settings_dict = runpy.run_module('dashboard.settings', run_name='__main__')
            default_db = settings_dict['DATABASES']['default']
            self.assertEqual(default_db['ENGINE'], 'django.db.backends.sqlite3')
            self.assertTrue(str(default_db['NAME']).endswith('db.sqlite3'))

    def test_evaluation_with_database_url_configures_postgresql(self):
        """3. APP_MODE=evaluation + DATABASE_URL -> Evaluation configuration works with PostgreSQL."""
        import os, runpy
        from unittest import mock

        env = os.environ.copy()
        env['APP_MODE'] = 'evaluation'
        env['DATABASE_URL'] = 'postgresql://postgres:secret@roundhouse.proxy.rlwy.net:5432/railway'
        with mock.patch.dict(os.environ, env, clear=True):
            settings_dict = runpy.run_module('dashboard.settings', run_name='__main__')
            default_db = settings_dict['DATABASES']['default']
            self.assertEqual(default_db['ENGINE'], 'django.db.backends.postgresql')
            self.assertEqual(default_db['NAME'], 'railway')

    def test_database_isolation_guard_preserves_403_route_protection(self):
        """4. The guard does not break existing 403 route protection."""
        from django.test import override_settings
        with override_settings(APP_MODE='evaluation'):
            url = reverse('predictor:feedback_experiment')
            res = self.client.get(url)
            self.assertEqual(res.status_code, 403)
            self.assertIn("Access Denied", res.content.decode())

    def test_evaluation_cannot_fallback_to_unsafe_development_database(self):
        """Inverse safety case: APP_MODE=evaluation cannot use development 'db.sqlite3'."""
        import os, runpy
        from unittest import mock
        from django.core.exceptions import ImproperlyConfigured

        env = os.environ.copy()
        env['APP_MODE'] = 'evaluation'
        env['DB_NAME'] = 'db.sqlite3'
        env.pop('DATABASE_URL', None)
        with mock.patch.dict(os.environ, env, clear=True):
            with self.assertRaises(ImproperlyConfigured) as ctx:
                runpy.run_module('dashboard.settings', run_name='__main__')
            self.assertIn("cannot use development database 'db.sqlite3'", str(ctx.exception))

    def test_feedback_lab_with_dedicated_database_url_configures_postgresql(self):
        """5. APP_MODE=feedback_lab + FEEDBACK_LAB_DATABASE_URL -> Dedicated Feedback Lab PostgreSQL works."""
        import os, runpy
        from unittest import mock

        env = os.environ.copy()
        env['APP_MODE'] = 'feedback_lab'
        env['FEEDBACK_LAB_DATABASE_URL'] = 'postgresql://postgres:secret@roundhouse.proxy.rlwy.net:5432/feedback_lab_db'
        env.pop('DATABASE_URL', None)
        with mock.patch.dict(os.environ, env, clear=True):
            settings_dict = runpy.run_module('dashboard.settings', run_name='__main__')
            default_db = settings_dict['DATABASES']['default']
            self.assertEqual(default_db['ENGINE'], 'django.db.backends.postgresql')
            self.assertEqual(default_db['NAME'], 'feedback_lab_db')

    def test_cross_database_url_collision_raises_improperly_configured(self):
        """6. Setting identical URLs between Evaluation and Feedback Lab raises ImproperlyConfigured."""
        import os, runpy
        from unittest import mock
        from django.core.exceptions import ImproperlyConfigured

        # Case A: Evaluation mode configured with FEEDBACK_LAB_DATABASE_URL identical to DATABASE_URL
        env = os.environ.copy()
        env['APP_MODE'] = 'evaluation'
        shared_url = 'postgresql://postgres:secret@roundhouse.proxy.rlwy.net:5432/shared_db'
        env['DATABASE_URL'] = shared_url
        env['FEEDBACK_LAB_DATABASE_URL'] = shared_url
        with mock.patch.dict(os.environ, env, clear=True):
            with self.assertRaises(ImproperlyConfigured) as ctx:
                runpy.run_module('dashboard.settings', run_name='__main__')
            self.assertIn("cannot point to the same production database URL", str(ctx.exception))

        # Case B: Feedback Lab mode configured with FEEDBACK_LAB_DATABASE_URL matching EVALUATION_DATABASE_URL
        env_fl = os.environ.copy()
        env_fl['APP_MODE'] = 'feedback_lab'
        env_fl['FEEDBACK_LAB_DATABASE_URL'] = shared_url
        env_fl['EVALUATION_DATABASE_URL'] = shared_url
        with mock.patch.dict(os.environ, env_fl, clear=True):
            with self.assertRaises(ImproperlyConfigured) as ctx:
                runpy.run_module('dashboard.settings', run_name='__main__')
            self.assertIn("Feedback Lab cannot connect to the Evaluation database URL", str(ctx.exception))


class LegacyRouteBlockingTests(TestCase):
    """Verifies that legacy single-stage endpoints return 404 in evaluation mode for participants."""

    @override_settings(APP_MODE='evaluation')
    def test_legacy_routes_blocked_in_evaluation_mode_for_participants(self):
        # 1. Dashboard legacy index form
        res = self.client.get(reverse('predictor:index'))
        self.assertEqual(res.status_code, 404)

        # 2. Components demo view
        res = self.client.get(reverse('predictor:components_demo'))
        self.assertEqual(res.status_code, 404)

        # 3. Model evaluation benchmark view
        res = self.client.get(reverse('predictor:evaluation'))
        self.assertEqual(res.status_code, 404)

        # 4. Predict POST endpoint
        res = self.client.post(reverse('predictor:predict'), {})
        self.assertEqual(res.status_code, 404)

        # 5. Override POST endpoint
        res = self.client.post(reverse('predictor:override'), {})
        self.assertEqual(res.status_code, 404)

    @override_settings(APP_MODE='evaluation')
    def test_legacy_routes_accessible_for_staff_in_evaluation_mode(self):
        from django.contrib.auth.models import User
        staff_user = User.objects.create_user(username='staff_test', password='password', is_staff=True)
        self.client.force_login(staff_user)

        res = self.client.get(reverse('predictor:components_demo'))
        self.assertEqual(res.status_code, 200)

        res = self.client.get(reverse('predictor:index'))
        self.assertEqual(res.status_code, 200)

    @override_settings(APP_MODE='feedback_lab')
    def test_legacy_routes_accessible_in_feedback_lab_mode(self):
        res = self.client.get(reverse('predictor:components_demo'))
        self.assertEqual(res.status_code, 200)

        res = self.client.get(reverse('predictor:index'))
        self.assertEqual(res.status_code, 200)


class EvaluationSessionScopingTests(TestCase):
    """
    Verifies participant scoping across evaluation sessions (Protocol E1 v1.0.3).
    Ensures session A cannot view, review, or assess cases belonging to session B,
    verifies count isolation, and confirms staff and feedback_lab are exempt.
    """

    def setUp(self):
        self.resp_a = EvaluationRespondent.objects.create(
            respondent_code="RESP-AAA",
            age_group="26-35",
            education_level="bachelor",
            technical_background="medium",
            health_background="none",
            consent_given=True,
            consent_timestamp=timezone.now(),
        )
        self.resp_b = EvaluationRespondent.objects.create(
            respondent_code="RESP-BBB",
            age_group="36-45",
            education_level="bachelor",
            technical_background="medium",
            health_background="none",
            consent_given=True,
            consent_timestamp=timezone.now(),
        )

        self.sess_a = EvaluationSession.objects.create(
            respondent=self.resp_a,
            session_token=str(uuid.uuid4()),
            status="in_progress",
            practice_completed=True,
        )
        self.sess_b = EvaluationSession.objects.create(
            respondent=self.resp_b,
            session_token=str(uuid.uuid4()),
            status="in_progress",
            practice_completed=True,
        )

        self.rec_a = ScreeningRecord.objects.create(
            age=45,
            sex="male",
            bmi=27.0,
            waist_cm=90.0,
            hypertension_history="no",
            smoking_history="no",
            sedentary_minutes_day=300,
            screening_probability=0.25,
            ai_referral_recommended=True,
            decision_threshold=Decimal("0.1389"),
            model_name="EBM_GAM_Stage1",
            evaluation_session=self.sess_a,
            is_practice=False,
        )
        ScreeningExplanation.objects.create(
            screening_record=self.rec_a,
            method="gam_native_additive",
            method_version="1.0",
            link_function="logit",
            intercept=0.0,
            contributions_json=[],
            reconstructed_linear_predictor=0.0,
            reconstructed_probability=0.25,
            reconstruction_error=0.0,
            model_sha256="fake_sha_a",
            status="generated",
        )

        self.rec_b = ScreeningRecord.objects.create(
            age=52,
            sex="female",
            bmi=31.0,
            waist_cm=96.0,
            hypertension_history="yes",
            smoking_history="no",
            sedentary_minutes_day=480,
            screening_probability=0.45,
            ai_referral_recommended=True,
            decision_threshold=Decimal("0.1389"),
            model_name="EBM_GAM_Stage1",
            evaluation_session=self.sess_b,
            is_practice=False,
        )
        ScreeningExplanation.objects.create(
            screening_record=self.rec_b,
            method="gam_native_additive",
            method_version="1.0",
            link_function="logit",
            intercept=0.0,
            contributions_json=[],
            reconstructed_linear_predictor=0.0,
            reconstructed_probability=0.45,
            reconstruction_error=0.0,
            model_sha256="fake_sha_b",
            status="generated",
        )

        self.client_a = Client(enforce_csrf_checks=True)
        s_a = self.client_a.session
        s_a['evaluation_session_token'] = str(self.sess_a.session_token)
        s_a['respondent_code'] = self.resp_a.respondent_code
        s_a.save()

        self.client_b = Client(enforce_csrf_checks=True)
        s_b = self.client_b.session
        s_b['evaluation_session_token'] = str(self.sess_b.session_token)
        s_b['respondent_code'] = self.resp_b.respondent_code
        s_b.save()

    def _get_csrf_token(self, client):
        req = RequestFactory().get('/')
        token = get_token(req)
        client.cookies['csrftoken'] = token
        return token

    @override_settings(APP_MODE='evaluation')
    def test_participant_a_cannot_get_participant_b_result(self):
        res_b = self.client_a.get(reverse('predictor:screening_result', args=[self.rec_b.id]))
        self.assertEqual(res_b.status_code, 404)

        res_a = self.client_a.get(reverse('predictor:screening_result', args=[self.rec_a.id]))
        self.assertEqual(res_a.status_code, 200)

    @override_settings(APP_MODE='evaluation')
    def test_participant_a_cannot_post_review_for_participant_b(self):
        csrf = self._get_csrf_token(self.client_a)
        initial_reviews = HumanReview.objects.count()

        # Attempt POST to unified review
        res_unified = self.client_a.post(
            reverse('predictor:unified_review', args=[self.rec_b.id]),
            {'csrfmiddlewaretoken': csrf, 'human_decision': 'accept'}
        )
        self.assertEqual(res_unified.status_code, 404)
        self.assertEqual(HumanReview.objects.count(), initial_reviews)

        # Attempt POST to accept review
        res_accept = self.client_a.post(
            reverse('predictor:accept_review', args=[self.rec_b.id]),
            {'csrfmiddlewaretoken': csrf, 'reviewer_code': self.resp_a.respondent_code}
        )
        self.assertEqual(res_accept.status_code, 404)
        self.assertEqual(HumanReview.objects.count(), initial_reviews)

        # Attempt POST to override review
        res_override = self.client_a.post(
            reverse('predictor:override_review', args=[self.rec_b.id]),
            {
                'csrfmiddlewaretoken': csrf,
                'reviewer_code': self.resp_a.respondent_code,
                'override_reason_code': 'clinical_judgement',
            }
        )
        self.assertEqual(res_override.status_code, 404)
        self.assertEqual(HumanReview.objects.count(), initial_reviews)

        self.rec_b.refresh_from_db()
        self.assertFalse(hasattr(self.rec_b, 'human_review') and self.rec_b.human_review is not None)

    @override_settings(APP_MODE='evaluation')
    def test_participant_a_cannot_post_stage2_for_participant_b(self):
        # Finalize a review on rec_b by B so stage 2 is otherwise eligible
        HumanReview.objects.create(
            screening_record=self.rec_b,
            reviewer_code=self.resp_b.respondent_code,
            review_action='accept',
            final_referral_recommended=True,
        )

        csrf = self._get_csrf_token(self.client_a)
        initial_stage2 = Stage2Assessment.objects.count()

        # GET Stage 2
        res_get = self.client_a.get(reverse('predictor:stage2', args=[self.rec_b.id]))
        self.assertEqual(res_get.status_code, 404)

        # POST Stage 2 entry (step 1)
        res_entry = self.client_a.post(
            reverse('predictor:stage2', args=[self.rec_b.id]),
            {'csrfmiddlewaretoken': csrf, 'hba1c_percent': '7.2'}
        )
        self.assertEqual(res_entry.status_code, 404)
        self.assertEqual(Stage2Assessment.objects.count(), initial_stage2)

        # POST Stage 2 confirm (step 2)
        res_confirm = self.client_a.post(
            reverse('predictor:stage2_confirm', args=[self.rec_b.id]),
            {'csrfmiddlewaretoken': csrf, 'hba1c_percent': '7.2'}
        )
        self.assertEqual(res_confirm.status_code, 404)
        self.assertEqual(Stage2Assessment.objects.count(), initial_stage2)

    @override_settings(APP_MODE='evaluation')
    def test_participant_sees_only_own_counts(self):
        # Overview view scoping
        res_a = self.client_a.get(reverse('predictor:overview'))
        self.assertEqual(res_a.context['total'], 1)
        self.assertEqual(res_a.context['recent_cases'][0]['record'].id, self.rec_a.id)

        res_b = self.client_b.get(reverse('predictor:overview'))
        self.assertEqual(res_b.context['total'], 1)
        self.assertEqual(res_b.context['recent_cases'][0]['record'].id, self.rec_b.id)

        # Review queue scoping
        rq_a = self.client_a.get(reverse('predictor:review_queue'))
        self.assertEqual(len(rq_a.context['pending_review_cases']), 1)
        self.assertEqual(rq_a.context['pending_review_cases'][0]['record'].id, self.rec_a.id)

        rq_b = self.client_b.get(reverse('predictor:review_queue'))
        self.assertEqual(len(rq_b.context['pending_review_cases']), 1)
        self.assertEqual(rq_b.context['pending_review_cases'][0]['record'].id, self.rec_b.id)

        # Analytics view scoping
        ana_a = self.client_a.get(reverse('predictor:analytics'))
        self.assertEqual(ana_a.context['analytics'].total_screenings, 1)

        ana_b = self.client_b.get(reverse('predictor:analytics'))
        self.assertEqual(ana_b.context['analytics'].total_screenings, 1)

    def test_staff_and_feedback_lab_unaffected(self):
        from django.contrib.auth.models import User
        staff_user = User.objects.create_user(username='staff_scope_test', password='password', is_staff=True)
        staff_client = Client()
        staff_client.force_login(staff_user)

        with override_settings(APP_MODE='evaluation'):
            res = staff_client.get(reverse('predictor:screening_result', args=[self.rec_b.id]))
            self.assertEqual(res.status_code, 200)

            ov = staff_client.get(reverse('predictor:overview'))
            self.assertEqual(ov.context['total'], 2)

        fb_client = Client()
        with override_settings(APP_MODE='feedback_lab'):
            res = fb_client.get(reverse('predictor:screening_result', args=[self.rec_b.id]))
            self.assertEqual(res.status_code, 200)

            ov = fb_client.get(reverse('predictor:overview'))
            self.assertEqual(ov.context['total'], 2)


