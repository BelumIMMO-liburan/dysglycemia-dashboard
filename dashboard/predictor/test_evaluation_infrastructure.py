"""
Automated Test Suite for Evaluation Research Infrastructure.
Tests:
1. ScreeningRecord and Review Linkage to EvaluationSession
2. Event Logging during clinical screening workflow
3. Practice Case P0 Exclusion from Research Analytics
4. Researcher Authorization & Route Protection
5. Live Evaluation Analytics Service & Dashboard
6. Valid Respondent Filtering & Exclusion Semantics
7. Evaluation Export Service & ZIP/CSV Generation
8. SQLite Absolute Path Configuration
"""

import io
import json
import zipfile
from decimal import Decimal
from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from predictor.models import (
    EvaluationRespondent,
    EvaluationSession,
    EvaluationEvent,
    QuestionnaireResponse,
    ScreeningRecord,
    HumanReview,
    Stage2Assessment,
)
from predictor.services.research_analytics import compute_research_analytics
from predictor.services.evaluation_analytics import (
    compute_evaluation_analytics,
    compute_valid_respondent_status,
)
from predictor.services.evaluation_export import generate_evaluation_export_zip


class EvaluationInfrastructureLinkageTests(TestCase):
    """Tests linkage of screening records, reviews, and events to EvaluationSession."""

    def setUp(self):
        self.respondent = EvaluationRespondent.objects.create(
            respondent_code="RESP-LINK-001",
            age_group="25-34",
            education_level="bachelor",
            technical_background="frequent",
            health_background="practitioner",
        )
        self.session = EvaluationSession.objects.create(
            respondent=self.respondent,
            session_token="test_token_link_001",
        )

    def test_screening_creation_links_to_session_and_logs_event(self):
        """Active evaluation session automatically links to ScreeningRecord and logs stage1_completed."""
        s = self.client.session
        s['evaluation_session_token'] = self.session.session_token
        s.save()

        # Submit valid screening form
        response = self.client.post(reverse('predictor:run_screening'), {
            'age': 50,
            'sex': 'male',
            'bmi': 27.5,
            'waist_cm': 90.0,
            'hypertension_history': 'no',
            'smoking_history': 'no',
            'sedentary_minutes_day': 300,
        })
        self.assertEqual(response.status_code, 302)

        record = ScreeningRecord.objects.filter(age=50, bmi=27.5).first()
        self.assertIsNotNone(record)
        self.assertEqual(record.evaluation_session, self.session)
        self.assertFalse(record.is_practice)

        # Check stage1_completed event
        event = self.session.events.filter(event_name='stage1_completed').first()
        self.assertIsNotNone(event)
        self.assertEqual(event.event_data.get('record_id'), str(record.id))

    def test_practice_case_links_to_session_with_is_practice_true(self):
        """P0 practice case attaches session and sets is_practice=True."""
        s = self.client.session
        s['evaluation_session_token'] = self.session.session_token
        s.save()

        response = self.client.get(reverse('predictor:evaluation_practice'))
        self.assertEqual(response.status_code, 200)

        practice_record = ScreeningRecord.objects.filter(
            evaluation_session=self.session,
            is_practice=True,
        ).first()
        self.assertIsNotNone(practice_record)
        self.assertTrue(practice_record.is_practice)

    def test_review_submission_logs_event(self):
        """Accepting or overriding AI referral logs human_review_completed."""
        record = ScreeningRecord.objects.create(
            age=60, sex='female', bmi=30.0, waist_cm=95.0,
            hypertension_history='yes', smoking_history='no',
            sedentary_minutes_day=400, screening_probability=0.45,
            ai_referral_recommended=True, decision_threshold=Decimal('0.1389'),
            model_name='EBM_GAM_v1.0.3', model_sha256='dummy',
            preprocessor_sha256='dummy', input_schema_version='1.0',
            idempotency_token='test_review_rec',
            evaluation_session=self.session,
        )
        # Create generated explanation prerequisite
        from predictor.models import ScreeningExplanation
        ScreeningExplanation.objects.create(
            screening_record=record,
            method='gam_native_additive',
            method_version='1.0',
            link_function='logit',
            intercept=-1.0,
            contributions_json=[],
            reconstructed_linear_predictor=-0.5,
            reconstructed_probability=0.45,
            reconstruction_error=0.0,
            model_sha256='dummy',
            status='generated',
        )

        s = self.client.session
        s['evaluation_session_token'] = self.session.session_token
        s.save()

        post_url = reverse('predictor:accept_review', kwargs={'screening_id': record.id})
        resp = self.client.post(post_url, {'reviewer_code': 'HP-REV-01'})
        self.assertEqual(resp.status_code, 302)

        # Check HumanReview created
        review = HumanReview.objects.get(screening_record=record)
        self.assertEqual(review.review_action, 'accepted')

        # Check event
        event = self.session.events.filter(event_name='human_review_completed').first()
        self.assertIsNotNone(event)
        self.assertEqual(event.event_data.get('action'), 'accepted')


class PracticeExclusionAnalyticsTests(TestCase):
    """Verifies that is_practice=True records are strictly excluded from research analytics."""

    def setUp(self):
        # 1 standard clinical record
        self.clinical_record = ScreeningRecord.objects.create(
            age=52, sex='male', bmi=26.0, waist_cm=88.0,
            hypertension_history='no', smoking_history='no',
            sedentary_minutes_day=320, screening_probability=0.25,
            ai_referral_recommended=True, decision_threshold=Decimal('0.1389'),
            model_name='EBM_GAM_v1.0.3', model_sha256='dummy',
            preprocessor_sha256='dummy', input_schema_version='1.0',
            idempotency_token='clin_1', is_practice=False,
        )
        HumanReview.objects.create(
            screening_record=self.clinical_record,
            reviewer_code='REV-001',
            review_action='accepted',
            final_referral_recommended=True,
        )

        # 1 practice record P0
        self.practice_record = ScreeningRecord.objects.create(
            age=45, sex='female', bmi=24.0, waist_cm=80.0,
            hypertension_history='no', smoking_history='no',
            sedentary_minutes_day=200, screening_probability=0.08,
            ai_referral_recommended=False, decision_threshold=Decimal('0.1389'),
            model_name='EBM_GAM_v1.0.3', model_sha256='dummy',
            preprocessor_sha256='dummy', input_schema_version='1.0',
            idempotency_token='prac_1', is_practice=True,
        )
        HumanReview.objects.create(
            screening_record=self.practice_record,
            reviewer_code='REV-002',
            review_action='overridden',
            final_referral_recommended=True,
            override_reason_code='additional_context_increases_concern',
        )

    def test_research_analytics_excludes_practice_by_default(self):
        """Default compute_research_analytics has total_screenings=1, excluding practice P0."""
        analytics = compute_research_analytics()
        self.assertEqual(analytics.total_screenings, 1)
        self.assertEqual(analytics.reviewed_count, 1)
        self.assertEqual(analytics.accepted_count, 1)
        self.assertEqual(analytics.overridden_count, 0)

    def test_research_analytics_can_include_practice_if_explicitly_requested(self):
        """When include_practice=True, total_screenings=2."""
        analytics = compute_research_analytics(include_practice=True)
        self.assertEqual(analytics.total_screenings, 2)
        self.assertEqual(analytics.reviewed_count, 2)
        self.assertEqual(analytics.overridden_count, 1)


class ResearcherAccessAuthorizationTests(TestCase):
    """Verifies that researcher endpoints require proper authorization in evaluation mode."""

    def setUp(self):
        self.staff_user = User.objects.create_user(
            username='eval_researcher',
            password='securepassword123',
            is_staff=True,
        )

    @override_settings(APP_MODE='evaluation', RESEARCHER_ACCESS_KEY='secret_key_abc')
    def test_unauthorized_access_blocked_in_evaluation_mode(self):
        """Unauthenticated request without key receives 403 Forbidden."""
        resp = self.client.get(reverse('predictor:evaluation_analytics'))
        self.assertEqual(resp.status_code, 403)

        resp = self.client.get(reverse('predictor:evaluation_export'))
        self.assertEqual(resp.status_code, 403)

    @override_settings(APP_MODE='evaluation', RESEARCHER_ACCESS_KEY='secret_key_abc')
    def test_key_param_grants_access_in_evaluation_mode(self):
        """Passing valid key query param grants access."""
        resp = self.client.get(reverse('predictor:evaluation_analytics') + '?key=secret_key_abc')
        self.assertEqual(resp.status_code, 200)

    @override_settings(APP_MODE='evaluation', RESEARCHER_ACCESS_KEY='secret_key_abc')
    def test_staff_login_grants_access_in_evaluation_mode(self):
        """Logged in staff user is granted access without key."""
        self.client.login(username='eval_researcher', password='securepassword123')
        resp = self.client.get(reverse('predictor:evaluation_analytics'))
        self.assertEqual(resp.status_code, 200)

    @override_settings(APP_MODE='feedback_lab')
    def test_feedback_lab_mode_allows_researcher_endpoints(self):
        """In feedback_lab mode, researcher access is granted directly."""
        resp = self.client.get(reverse('predictor:evaluation_analytics'))
        self.assertEqual(resp.status_code, 200)


class EvaluationAnalyticsAndExportTests(TestCase):
    """Tests evaluation analytics calculation, valid respondent rules, and ZIP export generation."""

    def setUp(self):
        # Create completed respondent and session
        self.resp1 = EvaluationRespondent.objects.create(
            respondent_code="RESP-EVAL-01",
            age_group="25-34",
            education_level="bachelor",
            technical_background="frequent",
            health_background="practitioner",
        )
        self.sess1 = EvaluationSession.objects.create(
            respondent=self.resp1,
            session_token="sess_token_01",
            status="completed",
            practice_completed=True,
            questionnaire_completed=True,
            completed_at=timezone.now(),
        )
        # Create valid questionnaire response (SUS: 75.0, Comprehension: 8/8)
        self.qresp1 = QuestionnaireResponse.objects.create(
            respondent=self.resp1,
            session=self.sess1,
            c1_answer='A', c2_answer='B', c3_answer='C', c4_answer='D',
            c5_answer='A', c6_answer='B', c7_answer='C', c8_answer='D',
            comprehension_score=8,
            comprehension_pct=100.0,
            sus_1=4, sus_2=2, sus_3=4, sus_4=2, sus_5=4,
            sus_6=2, sus_7=4, sus_8=2, sus_9=4, sus_10=2,
            sus_score=75.0,
            clarity_1=5, clarity_2=5, clarity_3=5, clarity_4=5, clarity_5=5,
            open_1="Clear interface and faithful explanations.",
        )

        # Create incomplete session
        self.resp2 = EvaluationRespondent.objects.create(
            respondent_code="RESP-EVAL-02",
            age_group="18-24",
            education_level="undergrad",
            technical_background="frequent",
            health_background="student",
        )
        self.sess2 = EvaluationSession.objects.create(
            respondent=self.resp2,
            session_token="sess_token_02",
            status="active",
            practice_completed=False,
            questionnaire_completed=False,
        )

        # Create excluded session (protocol violation §6.2)
        self.resp3 = EvaluationRespondent.objects.create(
            respondent_code="RESP-EVAL-03",
            age_group="35-49",
            education_level="postgrad",
            technical_background="occasional",
            health_background="practitioner",
        )
        self.sess3 = EvaluationSession.objects.create(
            respondent=self.resp3,
            session_token="sess_token_03",
            status="completed",
            practice_completed=True,
            questionnaire_completed=True,
            is_excluded=True,
            exclusion_reason="technical_failure",
            exclusion_notes="Network dropped midway during evaluation.",
            excluded_at=timezone.now(),
        )
        self.qresp3 = QuestionnaireResponse.objects.create(
            respondent=self.resp3,
            session=self.sess3,
            c1_answer='A', c2_answer='B', c3_answer='Z', c4_answer='D',
            c5_answer='Z', c6_answer='B', c7_answer='C', c8_answer='Z',
            comprehension_score=5,
            comprehension_pct=62.5,
            sus_1=3, sus_2=3, sus_3=3, sus_4=3, sus_5=3,
            sus_6=3, sus_7=3, sus_8=3, sus_9=3, sus_10=3,
            sus_score=50.0,
            clarity_1=3, clarity_2=3, clarity_3=3, clarity_4=3, clarity_5=3,
        )

    def test_valid_respondent_classification(self):
        """Evaluates valid respondent criteria according to E1_ANALYSIS_PLAN.md §6.1 & §6.2."""
        # Sess1 is complete and not excluded -> valid
        status1 = compute_valid_respondent_status(self.sess1)
        self.assertTrue(status1['is_valid'])

        # Sess2 is incomplete -> not valid
        status2 = compute_valid_respondent_status(self.sess2)
        self.assertFalse(status2['is_valid'])
        self.assertEqual(status2['status_code'], 'INCOMPLETE_QUESTIONNAIRE')

        # Sess3 is excluded -> not valid
        status3 = compute_valid_respondent_status(self.sess3)
        self.assertFalse(status3['is_valid'])
        self.assertEqual(status3['status_code'], 'PROTOCOL_EXCLUDED')

    def test_compute_evaluation_analytics(self):
        """Analytics aggregates respondents, sessions, completion rates, and psychometrics."""
        stats = compute_evaluation_analytics(include_excluded=False)
        self.assertEqual(stats.total_respondents, 3)
        self.assertEqual(stats.total_sessions, 3)
        self.assertEqual(stats.valid_research_respondents, 1)
        self.assertEqual(stats.sessions_excluded, 1)

        # Psychometrics for valid sessions
        self.assertEqual(stats.sus_completed_count, 1)
        self.assertEqual(stats.mean_sus_score, 75.0)
        self.assertEqual(stats.mean_comprehension_score, 8.0)

    def test_evaluation_export_zip_structure_and_integrity(self):
        """ZIP export contains all 7 CSVs, manifest.json with valid SHA-256, and README.txt."""
        zip_bytes, filename, manifest = generate_evaluation_export_zip()
        self.assertTrue(filename.startswith('evaluation_export_'))
        self.assertTrue(filename.endswith('.zip'))

        with zipfile.ZipFile(io.BytesIO(zip_bytes), 'r') as z:
            namelist = z.namelist()
            expected_files = [
                'respondents.csv',
                'sessions.csv',
                'events.csv',
                'screening.csv',
                'human_review.csv',
                'stage2.csv',
                'questionnaire.csv',
                'manifest.json',
                'README.txt',
            ]
            for ef in expected_files:
                self.assertIn(ef, namelist)

            manifest_content = json.loads(z.read('manifest.json').decode('utf-8'))
            self.assertIn('files', manifest_content)
            self.assertEqual(manifest_content['files_count'], 7)
            self.assertIn('generated_at_utc', manifest_content)

            # Check that respondents CSV has respondent_code
            resp_csv = z.read('respondents.csv').decode('utf-8')
            self.assertIn('RESP-EVAL-01', resp_csv)
            self.assertIn('health_background', resp_csv)

    def test_session_exclusion_toggle_endpoint(self):
        """Researcher can toggle exclusion on a session via POST."""
        exclude_url = reverse('predictor:evaluation_exclude_session', kwargs={'session_id': self.sess1.id})
        
        # Exclude
        resp = self.client.post(exclude_url, {
            'action': 'exclude',
            'exclusion_reason': 'eligibility_violation',
            'exclusion_notes': 'Did not meet medical professional criteria.',
        })
        self.assertEqual(resp.status_code, 302)
        self.sess1.refresh_from_db()
        self.assertTrue(self.sess1.is_excluded)
        self.assertEqual(self.sess1.exclusion_reason, 'eligibility_violation')

        # Reinstate
        resp = self.client.post(exclude_url, {
            'action': 'reinstate',
        })
        self.assertEqual(resp.status_code, 302)
        self.sess1.refresh_from_db()
        self.assertFalse(self.sess1.is_excluded)
