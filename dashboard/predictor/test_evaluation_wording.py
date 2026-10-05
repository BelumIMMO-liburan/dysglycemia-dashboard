"""
Automated tests for participant evaluation mode wording alignment and researcher wording preservation.
Verifies that all participant-facing routes in APP_MODE=evaluation are strictly purged of
unsupported claims (clinician, analyzed via NLP, learning signal, Reviewer Code, laboratory measurement)
and that feedback_lab mode retains its canonical researcher terminology.
"""

from decimal import Decimal
import uuid
from django.test import TestCase, override_settings
from django.urls import reverse

from predictor.models import (
    ScreeningRecord,
    ScreeningExplanation,
    HumanReview,
    Stage2Assessment,
    EvaluationRespondent,
    EvaluationSession,
)


class EvaluationModeWordingTests(TestCase):
    """
    Renders every participant route in APP_MODE=evaluation and asserts ABSENCE of prohibited strings
    and PRESENCE of required frozen-model governance notices.
    """

    PROHIBITED_STRINGS = [
        "clinician",
        "clinical review",
        "analyzed via NLP",
        "generate the learning signal",
        "Structured Learning Signal",
        "Reviewer Code",
        "laboratory measurement",
    ]

    def setUp(self):
        # 1. Onboarding Respondent and Session (unlocked practice)
        self.respondent = EvaluationRespondent.objects.create(
            respondent_code="R-TEST-W01",
            age_group="25-34",
            education_level="sarjana",
            technical_background="intermediate",
            health_background="layperson",
            consent_given=True,
        )
        self.session_token = uuid.uuid4().hex
        self.session = EvaluationSession.objects.create(
            respondent=self.respondent,
            session_token=self.session_token,
            app_version="v1.0.3",
            model_version="GAM-v1",
            status="in_progress",
            practice_completed=True,
            questionnaire_completed=False,
        )

        # 2. Case 1: Pending Human Review (Elevated referral)
        self.rec_pending = ScreeningRecord.objects.create(
            id=uuid.uuid4(),
            age=52,
            sex="male",
            bmi=Decimal("28.4"),
            waist_cm=Decimal("98.5"),
            hypertension_history="yes",
            smoking_history="no",
            sedentary_minutes_day=480,
            screening_probability=0.2500,
            ai_referral_recommended=True,
            decision_threshold=Decimal("0.1389"),
            model_name="GAM-v1",
            model_sha256="test_sha",
            preprocessor_sha256="test_sha",
            input_schema_version="1.0",
            is_practice=False,
            evaluation_session=self.session,
        )
        ScreeningExplanation.objects.create(
            screening_record=self.rec_pending,
            method="gam_native_additive",
            method_version="1.0",
            link_function="logit",
            intercept=-1.5,
            contributions_json=[],
            reconstructed_linear_predictor=-1.1,
            reconstructed_probability=0.2500,
            reconstruction_error=0.0001,
            model_sha256="test_sha",
            status="generated",
        )

        # 3. Case 2: Finalized Override Card
        self.rec_overridden = ScreeningRecord.objects.create(
            id=uuid.uuid4(),
            age=45,
            sex="female",
            bmi=Decimal("29.0"),
            waist_cm=Decimal("92.0"),
            hypertension_history="no",
            smoking_history="no",
            sedentary_minutes_day=300,
            screening_probability=0.1800,
            ai_referral_recommended=True,
            decision_threshold=Decimal("0.1389"),
            model_name="GAM-v1",
            model_sha256="test_sha",
            preprocessor_sha256="test_sha",
            input_schema_version="1.0",
            is_practice=False,
            evaluation_session=self.session,
        )
        ScreeningExplanation.objects.create(
            screening_record=self.rec_overridden,
            method="gam_native_additive",
            method_version="1.0",
            link_function="logit",
            intercept=-1.5,
            contributions_json=[],
            reconstructed_linear_predictor=-1.5,
            reconstructed_probability=0.1800,
            reconstruction_error=0.0001,
            model_sha256="test_sha",
            status="generated",
        )
        HumanReview.objects.create(
            screening_record=self.rec_overridden,
            review_action="overridden",
            reviewer_code="R-TEST-W01",
            final_referral_recommended=False,
            override_reason_code="bmi_overweighted",
            override_note="Athlete with high muscularity.",
        )

        # 4. Case 3: Accepted Referral awaiting Stage 2
        self.rec_stage2_pending = ScreeningRecord.objects.create(
            id=uuid.uuid4(),
            age=60,
            sex="male",
            bmi=Decimal("31.0"),
            waist_cm=Decimal("102.0"),
            hypertension_history="yes",
            smoking_history="yes",
            sedentary_minutes_day=500,
            screening_probability=0.3500,
            ai_referral_recommended=True,
            decision_threshold=Decimal("0.1389"),
            model_name="GAM-v1",
            model_sha256="test_sha",
            preprocessor_sha256="test_sha",
            input_schema_version="1.0",
            is_practice=False,
            evaluation_session=self.session,
        )
        ScreeningExplanation.objects.create(
            screening_record=self.rec_stage2_pending,
            method="gam_native_additive",
            method_version="1.0",
            link_function="logit",
            intercept=-1.5,
            contributions_json=[],
            reconstructed_linear_predictor=-0.6,
            reconstructed_probability=0.3500,
            reconstruction_error=0.0001,
            model_sha256="test_sha",
            status="generated",
        )
        HumanReview.objects.create(
            screening_record=self.rec_stage2_pending,
            review_action="accepted",
            reviewer_code="R-TEST-W01",
            final_referral_recommended=True,
        )

        # 5. Case 4: Stage 2 Completed
        self.rec_stage2_completed = ScreeningRecord.objects.create(
            id=uuid.uuid4(),
            age=58,
            sex="female",
            bmi=Decimal("27.5"),
            waist_cm=Decimal("88.0"),
            hypertension_history="yes",
            smoking_history="no",
            sedentary_minutes_day=380,
            screening_probability=0.2200,
            ai_referral_recommended=True,
            decision_threshold=Decimal("0.1389"),
            model_name="GAM-v1",
            model_sha256="test_sha",
            preprocessor_sha256="test_sha",
            input_schema_version="1.0",
            is_practice=False,
            evaluation_session=self.session,
        )
        ScreeningExplanation.objects.create(
            screening_record=self.rec_stage2_completed,
            method="gam_native_additive",
            method_version="1.0",
            link_function="logit",
            intercept=-1.5,
            contributions_json=[],
            reconstructed_linear_predictor=-1.2,
            reconstructed_probability=0.2200,
            reconstruction_error=0.0001,
            model_sha256="test_sha",
            status="generated",
        )
        hr_comp = HumanReview.objects.create(
            screening_record=self.rec_stage2_completed,
            review_action="accepted",
            reviewer_code="R-TEST-W01",
            final_referral_recommended=True,
        )
        Stage2Assessment.objects.create(
            human_review=hr_comp,
            hba1c_percent=Decimal("6.20"),
            laboratory_range="prediabetes_range",
            range_rule_version="ADA-2026",
            entry_method="manual",
        )

        # Initialize client session with participant token
        session_data = self.client.session
        session_data['evaluation_session_token'] = self.session_token
        session_data['respondent_code'] = self.respondent.respondent_code
        session_data.save()

    def _assert_absence_of_prohibited_strings(self, response, route_name):
        """Helper to assert that none of the prohibited strings appear in rendered HTML."""
        content = response.content.decode("utf-8")
        for bad_str in self.PROHIBITED_STRINGS:
            self.assertNotIn(
                bad_str,
                content,
                f"Prohibited string '{bad_str}' found in route '{route_name}' under APP_MODE=evaluation!"
            )

    @override_settings(APP_MODE='evaluation')
    def test_overview_route_wording(self):
        """GET / (overview) in evaluation mode must not contain prohibited terms."""
        res = self.client.get(reverse('predictor:overview'))
        self.assertEqual(res.status_code, 200)
        self._assert_absence_of_prohibited_strings(res, "overview")
        self.assertContains(res, "Awaiting human review")
        self.assertContains(res, "Screenings requiring human review or Stage-2 HbA1c entry.")

    @override_settings(APP_MODE='evaluation')
    def test_new_screening_route_wording(self):
        """GET /screening/new/ in evaluation mode must not contain prohibited terms."""
        res = self.client.get(reverse('predictor:new_screening'))
        self.assertEqual(res.status_code, 200)
        self._assert_absence_of_prohibited_strings(res, "new_screening")

    @override_settings(APP_MODE='evaluation')
    def test_screening_result_pending_wording(self):
        """GET /screening/<id>/result/ with pending review in evaluation mode."""
        res = self.client.get(reverse('predictor:screening_result', kwargs={'screening_id': self.rec_pending.id}))
        self.assertEqual(res.status_code, 200)
        self._assert_absence_of_prohibited_strings(res, "screening_result_pending")
        
        # Verify required replacements
        self.assertContains(res, "Result Interpretation")
        self.assertContains(res, "record your review decision.")
        self.assertContains(res, "Stored for audit only; it does not change the model.")
        
        # Verify absence of reviewer code input in evaluation mode
        self.assertNotContains(res, "name=\"reviewer_code\"")
        
        # Assert PRESENCE on Human Review card of frozen model governance notice
        self.assertContains(
            res,
            "Evaluation Mode uses a frozen model. Human overrides are recorded for research analysis only and do not trigger model adaptation."
        )

    @override_settings(APP_MODE='evaluation')
    def test_screening_result_finalized_override_wording(self):
        """GET /screening/<id>/result/ with finalized override card in evaluation mode."""
        res = self.client.get(reverse('predictor:screening_result', kwargs={'screening_id': self.rec_overridden.id}))
        self.assertEqual(res.status_code, 200)
        self._assert_absence_of_prohibited_strings(res, "screening_result_finalized_override")
        
        # Finalized review card should label the identifier 'Reviewer ID' instead of 'Reviewer Code'
        self.assertContains(res, "Reviewer ID")
        self.assertNotContains(res, "Reviewer Code")
        self.assertNotContains(res, "Override Reason / Learning Signal")

        # ABSENCE checks for learning loop and adaptation in evaluation mode
        self.assertNotContains(res, "learning loop")
        self.assertNotContains(res, "adaptation layers")
        self.assertNotContains(res, "Check Similar Prior Cases")
        self.assertNotContains(res, "Eligible for Adaptation")

        # PRESENCE checks that finalized review summary still shows participant's decision
        self.assertContains(res, "Recommendation Overridden")
        self.assertContains(res, "No referral recommended at current operating point")
        self.assertContains(res, "Override Reason")
        self.assertContains(res, "Athlete with high muscularity.")

    @override_settings(APP_MODE='evaluation')
    def test_review_queue_route_wording(self):
        """GET /review/ in evaluation mode must not contain prohibited terms."""
        res = self.client.get(reverse('predictor:review_queue'))
        self.assertEqual(res.status_code, 200)
        self._assert_absence_of_prohibited_strings(res, "review_queue")
        self.assertContains(res, "Screenings with verified additive factor explanations awaiting human review.")

    @override_settings(APP_MODE='evaluation')
    def test_stage2_entry_route_wording(self):
        """GET /screening/<id>/stage2/ in evaluation mode must use range assessment wording."""
        res = self.client.get(reverse('predictor:stage2', kwargs={'screening_id': self.rec_stage2_pending.id}))
        self.assertEqual(res.status_code, 200)
        self._assert_absence_of_prohibited_strings(res, "stage2_entry")
        self.assertContains(res, "Stage 2 – HbA1c Range Assessment")
        self.assertContains(res, "Enter an HbA1c value for this exercise (hypothetical; not a laboratory result)")
        self.assertContains(res, "HbA1c value in percent (%)")

    @override_settings(APP_MODE='evaluation')
    def test_stage2_result_route_wording(self):
        """GET /screening/<id>/stage2/ (completed) in evaluation mode."""
        res = self.client.get(reverse('predictor:stage2', kwargs={'screening_id': self.rec_stage2_completed.id}))
        self.assertEqual(res.status_code, 200)
        self._assert_absence_of_prohibited_strings(res, "stage2_result")
        self.assertContains(res, "Stage 2 – HbA1c Range Assessment")
        self.assertContains(res, "ADA 2026 range categories")

    @override_settings(APP_MODE='evaluation')
    def test_practice_page_route_wording(self):
        """GET /evaluation/practice/ in evaluation mode must use revised Indonesian guidance."""
        res = self.client.get(reverse('predictor:evaluation_practice'))
        self.assertEqual(res.status_code, 200)
        self._assert_absence_of_prohibited_strings(res, "practice_page")
        self.assertContains(
            res,
            "Peninjau manusia memegang keputusan akhir: menerima rekomendasi atau melakukan Override dengan alasan terstruktur."
        )
        self.assertContains(
            res,
            "Pada Stage 2 Anda memasukkan satu nilai HbA1c hipotetik untuk menguji alur kerja. Ini bukan hasil laboratorium dan bukan diagnosis."
        )

    @override_settings(APP_MODE='evaluation')
    def test_about_route_wording(self):
        """GET /about/ in evaluation mode uses prototype study text without healthcare providers."""
        res = self.client.get(reverse('predictor:about'))
        self.assertEqual(res.status_code, 200)
        self._assert_absence_of_prohibited_strings(res, "about")
        self.assertNotContains(res, "assist healthcare providers")
        self.assertContains(
            res,
            "This dashboard is an academic research prototype and is not a medical diagnostic tool."
        )
        self.assertContains(
            res,
            "It is designed to prioritize non-laboratory community screening cases for possible Stage-2 laboratory evaluation, and to study how non-expert users understand the model's output and explanations."
        )
        self.assertContains(
            res,
            "In the participant evaluation, the review task was a simulated exercise performed by volunteers, mostly laypersons."
        )

    @override_settings(APP_MODE='evaluation')
    def test_analytics_route_wording(self):
        """GET /analytics/ in evaluation mode must use revised human reviewer table phrasing."""
        res = self.client.get(reverse('predictor:analytics'))
        self.assertEqual(res.status_code, 200)
        self._assert_absence_of_prohibited_strings(res, "analytics")
        self.assertContains(res, "human reviewer disposition")
        self.assertContains(res, "human reviewer decision override")
        self.assertContains(res, "human reviewer decision for Stage 2")

    @override_settings(APP_MODE='evaluation')
    def test_evaluation_mode_badge_wording(self):
        """Top bar badge in evaluation mode must display Mode Evaluasi without Model Beku."""
        res = self.client.get(reverse('predictor:overview'))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "Mode Evaluasi")
        self.assertContains(res, "Protocol v1.0.3")
        self.assertNotContains(res, "Model Beku")
        self.assertNotContains(res, "Feedback Lab · Localhost Mode")

    @override_settings(APP_MODE='evaluation')
    def test_server_autofill_reviewer_code_on_unified_review(self):
        """In evaluation mode, submitting review without reviewer_code auto-fills from respondent code."""
        post_url = reverse('predictor:unified_review', kwargs={'screening_id': self.rec_pending.id})
        post_data = {
            'human_decision': 'override',
            'override_factor': 'bmi_overweighted',
            'rationale': 'Participant override test rationale.',
        }
        res = self.client.post(post_url, post_data)
        self.assertEqual(res.status_code, 302)
        
        self.rec_pending.refresh_from_db()
        self.assertTrue(hasattr(self.rec_pending, 'human_review'))
        hr = self.rec_pending.human_review
        self.assertEqual(hr.review_action, 'overridden')
        self.assertEqual(hr.reviewer_code, self.respondent.respondent_code)
        self.assertEqual(hr.override_reason_code, 'bmi_overweighted')

    @override_settings(APP_MODE='feedback_lab')
    def test_feedback_lab_mode_retains_original_researcher_wording(self):
        """In feedback_lab mode, the template must continue showing original learning signal wording."""
        res = self.client.get(reverse('predictor:screening_result', kwargs={'screening_id': self.rec_pending.id}))
        self.assertEqual(res.status_code, 200)
        
        # Researcher wording must be present in feedback_lab mode
        self.assertContains(res, "Structured Learning Signal")
        self.assertContains(res, "Reviewer Code")
        self.assertContains(res, "canonical input for the residual adaptation layer")
        self.assertContains(
            res,
            "Human overrides generate the learning signal directly within this unified review action."
        )
        self.assertContains(res, "<strong>Feedback Lab</strong> · Localhost Mode")
