"""
Unit and Integration Tests for Stage-1 Screening Form
Phase D2.2 Verification Suite

Tests strict server-side validation, supported development-domain ranges,
missing value rejection, input review state rendering, and isolation from
machine learning inference.
"""

from django.test import TestCase, Client
from django.urls import reverse
from django.core.exceptions import ValidationError
from .forms import Stage1ScreeningForm
from .models import Prediction, Override
from .screening_schema import STAGE1_INPUT_SCHEMA


class Stage1ScreeningFormUnitTests(TestCase):
    """Unit tests for Stage1ScreeningForm validation logic."""

    def setUp(self):
        self.valid_payload = {
            'age': 52,
            'sex': 'male',
            'bmi': 28.4,
            'waist_cm': 98.5,
            'hypertension_history': 'yes',
            'smoking_history': 'no',
            'sedentary_minutes_day': 480,
        }

    def test_valid_payload_passes(self):
        """A complete, valid payload matching research bounds must pass."""
        form = Stage1ScreeningForm(data=self.valid_payload)
        self.assertTrue(form.is_valid(), msg=f"Form errors: {form.errors}")
        summary = form.get_sanitized_summary()
        self.assertIsNotNone(summary)
        self.assertEqual(len(summary), 7)
        # Check specific field outputs
        age_entry = next(item for item in summary if item['canonical_name'] == 'age')
        self.assertEqual(age_entry['display_value'], '52 years')
        bmi_entry = next(item for item in summary if item['canonical_name'] == 'bmi')
        self.assertEqual(bmi_entry['display_value'], '28.4 kg/m²')

    def test_all_fields_are_required(self):
        """All 7 Stage-1 fields are mandatory; empty submissions must fail."""
        form = Stage1ScreeningForm(data={})
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 7)
        for field_name in STAGE1_INPUT_SCHEMA.keys():
            self.assertIn(field_name, form.errors)

    def test_age_boundaries(self):
        """Age must be between 18 and 80 inclusive."""
        # Lower bound: 18 is valid, 17 is invalid
        payload = self.valid_payload.copy()
        payload['age'] = 18
        self.assertTrue(Stage1ScreeningForm(data=payload).is_valid())

        payload['age'] = 17
        f = Stage1ScreeningForm(data=payload)
        self.assertFalse(f.is_valid())
        self.assertIn('age', f.errors)

        # Upper bound: 80 is valid, 81 is invalid
        payload['age'] = 80
        self.assertTrue(Stage1ScreeningForm(data=payload).is_valid())

        payload['age'] = 81
        f = Stage1ScreeningForm(data=payload)
        self.assertFalse(f.is_valid())
        self.assertIn('age', f.errors)

    def test_sex_choices(self):
        """Sex only accepts 'male' or 'female' based on the frozen model factor."""
        payload = self.valid_payload.copy()
        payload['sex'] = 'female'
        self.assertTrue(Stage1ScreeningForm(data=payload).is_valid())

        payload['sex'] = 'other'
        f = Stage1ScreeningForm(data=payload)
        self.assertFalse(f.is_valid())
        self.assertIn('sex', f.errors)

    def test_bmi_boundaries(self):
        """BMI must be between 11.1 and 69.9 kg/m²."""
        payload = self.valid_payload.copy()
        payload['bmi'] = 11.1
        self.assertTrue(Stage1ScreeningForm(data=payload).is_valid())

        payload['bmi'] = 11.0
        f = Stage1ScreeningForm(data=payload)
        self.assertFalse(f.is_valid())
        self.assertIn('bmi', f.errors)

        payload['bmi'] = 69.9
        self.assertTrue(Stage1ScreeningForm(data=payload).is_valid())

        payload['bmi'] = 70.0
        f = Stage1ScreeningForm(data=payload)
        self.assertFalse(f.is_valid())
        self.assertIn('bmi', f.errors)

    def test_waist_boundaries(self):
        """Waist circumference must be between 60.0 and 187.0 cm."""
        payload = self.valid_payload.copy()
        payload['waist_cm'] = 60.0
        self.assertTrue(Stage1ScreeningForm(data=payload).is_valid())

        payload['waist_cm'] = 59.9
        f = Stage1ScreeningForm(data=payload)
        self.assertFalse(f.is_valid())
        self.assertIn('waist_cm', f.errors)

        payload['waist_cm'] = 187.0
        self.assertTrue(Stage1ScreeningForm(data=payload).is_valid())

        payload['waist_cm'] = 187.1
        f = Stage1ScreeningForm(data=payload)
        self.assertFalse(f.is_valid())
        self.assertIn('waist_cm', f.errors)

    def test_hypertension_history_choices(self):
        """Hypertension history only accepts 'yes' or 'no'."""
        payload = self.valid_payload.copy()
        payload['hypertension_history'] = 'no'
        self.assertTrue(Stage1ScreeningForm(data=payload).is_valid())

        payload['hypertension_history'] = 'diagnosed_recently'
        f = Stage1ScreeningForm(data=payload)
        self.assertFalse(f.is_valid())
        self.assertIn('hypertension_history', f.errors)

    def test_smoking_history_choices(self):
        """Smoking history only accepts 'yes' or 'no'."""
        payload = self.valid_payload.copy()
        payload['smoking_history'] = 'yes'
        self.assertTrue(Stage1ScreeningForm(data=payload).is_valid())

        payload['smoking_history'] = 'current_smoker'
        f = Stage1ScreeningForm(data=payload)
        self.assertFalse(f.is_valid())
        self.assertIn('smoking_history', f.errors)

    def test_sedentary_minutes_boundaries_and_sentinels(self):
        """Sedentary time must be 0-1200 min/day; sentinel codes 7777 and 9999 rejected."""
        payload = self.valid_payload.copy()
        payload['sedentary_minutes_day'] = 0
        self.assertTrue(Stage1ScreeningForm(data=payload).is_valid())

        payload['sedentary_minutes_day'] = 1200
        self.assertTrue(Stage1ScreeningForm(data=payload).is_valid())

        # Negative values rejected
        payload['sedentary_minutes_day'] = -10
        f = Stage1ScreeningForm(data=payload)
        self.assertFalse(f.is_valid())
        self.assertIn('sedentary_minutes_day', f.errors)

        # Above max rejected
        payload['sedentary_minutes_day'] = 1201
        f = Stage1ScreeningForm(data=payload)
        self.assertFalse(f.is_valid())
        self.assertIn('sedentary_minutes_day', f.errors)

        # NHANES sentinel missing codes rejected
        for sentinel in [7777, 9999]:
            payload['sedentary_minutes_day'] = sentinel
            f = Stage1ScreeningForm(data=payload)
            self.assertFalse(f.is_valid())
            self.assertIn('sedentary_minutes_day', f.errors)


class Stage1ScreeningViewIntegrationTests(TestCase):
    """Integration tests for GET and POST endpoints at /screening/new/."""

    def setUp(self):
        self.client = Client()
        self.url = reverse('predictor:new_screening')
        self.valid_payload = {
            'age': 52,
            'sex': 'male',
            'bmi': 28.4,
            'waist_cm': 98.5,
            'hypertension_history': 'yes',
            'smoking_history': 'no',
            'sedentary_minutes_day': 480,
        }

    def test_get_new_screening_page(self):
        """GET request returns HTTP 200 and renders empty Stage-1 form surface."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')
        self.assertIn('Stage-1 Non-Laboratory Screening Form', content)
        self.assertIn('Age', content)
        self.assertIn('Biological Sex', content)
        self.assertIn('Body Mass Index (BMI)', content)
        self.assertIn('Waist Circumference', content)
        self.assertIn('History of Hypertension', content)
        self.assertIn('Smoking History', content)
        self.assertIn('Sedentary Time', content)
        self.assertIn('Review Inputs', content)

    def test_valid_post_renders_input_review_state(self):
        """Valid POST renders Input Review State and preserves parameters without DB write."""
        initial_prediction_count = Prediction.objects.count()
        response = self.client.post(self.url, data=self.valid_payload)
        self.assertEqual(response.status_code, 200)

        content = response.content.decode('utf-8')
        self.assertIn('Inputs Validated Successfully', content)
        self.assertIn('Stage-1 Input Parameter Summary', content)
        self.assertIn('52 years', content)
        self.assertIn('Male', content)
        self.assertIn('28.4 kg/m²', content)
        self.assertIn('98.5 cm', content)
        self.assertIn('480 minutes/day', content)
        self.assertIn('Edit Inputs', content)
        self.assertIn('Run Screening', content)

        # Confirm ZERO database rows created
        self.assertEqual(Prediction.objects.count(), initial_prediction_count)
        self.assertEqual(Override.objects.count(), 0)

        # Confirm NO screening inference probability rendered
        self.assertNotIn('ELEVATED SCREENING SIGNAL', content)
        self.assertNotIn('LOWER SCREENING SIGNAL', content)
        self.assertNotIn('0.1389', content)

    def test_invalid_post_renders_error_summary_and_field_errors(self):
        """Invalid POST renders accessible error summary and keeps user on form."""
        invalid_payload = self.valid_payload.copy()
        invalid_payload['age'] = 99  # Out of bounds (>80)
        invalid_payload['sedentary_minutes_day'] = 7777  # Sentinel code

        response = self.client.post(self.url, data=invalid_payload)
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')

        # Error summary must appear
        self.assertIn('Please review 2 input fields', content)
        self.assertIn('id="error-summary"', content)
        self.assertIn('aria-invalid="true"', content)
        # Inputs not in error state should be preserved
        self.assertIn('value="28.4"', content)
        self.assertIn('value="98.5"', content)


# ==============================================================================
# PHASE D2.3 TEST SUITE: FROZEN GAM INFERENCE ADAPTER INTEGRATION
# ==============================================================================

import unittest.mock as mock
from .services import screening_inference
from .services.screening_inference import (
    ScreeningInferenceService,
    ScreeningInferenceResult,
    ArtifactIntegrityError,
    ScreeningInferenceError,
    FROZEN_DECISION_THRESHOLD,
    GAM_MODEL_SHA256,
    PREPROCESSOR_SHA256,
)


class ScreeningInferenceAdapterUnitTests(TestCase):
    """Unit tests for the frozen GAM model inference adapter service."""

    def setUp(self):
        self.adapter = screening_inference.get_inference_adapter()
        self.valid_input = {
            'age': 52,
            'sex': 'male',
            'bmi': 28.4,
            'waist_cm': 98.5,
            'hypertension_history': 'yes',
            'smoking_history': 'no',
            'sedentary_minutes_day': 480,
        }

    def test_artifact_hashes_integrity(self):
        """Adapter must verify SHA256 hashes against canonical baselines."""
        gam_hash, prep_hash = self.adapter.verify_integrity()
        self.assertEqual(gam_hash, GAM_MODEL_SHA256)
        self.assertEqual(prep_hash, PREPROCESSOR_SHA256)

    def test_corrupt_hash_raises_integrity_error(self):
        """Tampered or mismatching hashes must halt inference immediately."""
        with mock.patch('predictor.services.screening_inference.compute_file_sha256', return_value="0000000000000000000000000000000000000000000000000000000000000000"):
            with self.assertRaises(ArtifactIntegrityError):
                screening_inference.verify_artifact_integrity()

    def test_deterministic_prediction_execution(self):
        """Valid inputs produce a valid ScreeningInferenceResult with strict fields."""
        result = self.adapter.predict(self.valid_input)
        self.assertIsInstance(result, ScreeningInferenceResult)
        self.assertGreaterEqual(result.screening_probability, 0.0)
        self.assertLessEqual(result.screening_probability, 1.0)
        self.assertEqual(result.decision_threshold, FROZEN_DECISION_THRESHOLD)
        self.assertIn(result.preliminary_decision, ['REFER', 'ROUTINE'])
        self.assertIn('Phase-5 GAM', result.model_version)
        self.assertIn('FrozenPreprocessor', result.preprocessor_version)
        self.assertEqual(len(result.raw_transformed_vector), 7)

    def test_threshold_comparison_exactness(self):
        """Evaluate exact floating-point decision boundary without premature rounding."""
        # Test exact threshold logic
        test_vector = [0.0] * 7

        # Case 1: Probability exactly at threshold (0.1389)
        with mock.patch.object(self.adapter._gam, 'predict_mu', return_value=[0.1389]):
            res = self.adapter.predict(self.valid_input)
            self.assertEqual(res.preliminary_decision, 'REFER')
            self.assertIn('Refer for Stage-2', res.preliminary_recommendation)

        # Case 2: Probability strictly below threshold (0.1388999999)
        with mock.patch.object(self.adapter._gam, 'predict_mu', return_value=[0.1388999999]):
            res = self.adapter.predict(self.valid_input)
            self.assertEqual(res.preliminary_decision, 'ROUTINE')
            self.assertIn('Routine Care', res.preliminary_recommendation)

    def test_semantic_factor_encoding(self):
        """Strictly maps clinical semantics to binary floats (male=1, female=0, yes=1, no=0)."""
        # Male, yes, no
        res1 = self.adapter.predict({
            'age': 45, 'sex': 'male', 'bmi': 25.0, 'waist_cm': 90.0,
            'hypertension_history': 'yes', 'smoking_history': 'no', 'sedentary_minutes_day': 300
        })
        # Female, no, yes
        res2 = self.adapter.predict({
            'age': 45, 'sex': 'female', 'bmi': 25.0, 'waist_cm': 90.0,
            'hypertension_history': 'no', 'smoking_history': 'yes', 'sedentary_minutes_day': 300
        })
        self.assertEqual(res1.raw_transformed_vector[1], 1.0)  # sex
        self.assertEqual(res1.raw_transformed_vector[3], 1.0)  # hypertension
        self.assertEqual(res1.raw_transformed_vector[4], 0.0)  # smoking

        self.assertEqual(res2.raw_transformed_vector[1], 0.0)  # sex
        self.assertEqual(res2.raw_transformed_vector[3], 0.0)  # hypertension
        self.assertEqual(res2.raw_transformed_vector[4], 1.0)  # smoking

    def test_malformed_inputs_rejected(self):
        """Inference adapter defensively rejects missing keys or illegal types."""
        incomplete = self.valid_input.copy()
        del incomplete['age']
        with self.assertRaises(ScreeningInferenceError):
            self.adapter.predict(incomplete)

        bad_type = self.valid_input.copy()
        bad_type['sex'] = 'invalid_choice'
        with self.assertRaises(ScreeningInferenceError):
            self.adapter.predict(bad_type)

    def test_preprocessor_is_transform_only(self):
        """Preprocessor must never re-fit; scaler mean and variance must remain constant."""
        scaler = self.adapter._preprocessor.scaler
        original_mean = scaler.mean_.copy()
        original_scale = scaler.scale_.copy()

        # Run prediction
        self.adapter.predict(self.valid_input)

        # Assert parameters are untouched
        import numpy as np
        np.testing.assert_array_equal(scaler.mean_, original_mean)
        np.testing.assert_array_equal(scaler.scale_, original_scale)

    def test_development_parity_precision(self):
        """
        Verify development parity: Direct GAM prediction vs adapter prediction
        must match with absolute difference <= 1e-12.
        """
        # Formulate a set of diverse test cases across valid development ranges
        test_cases = [
            {'age': 25, 'sex': 'female', 'bmi': 19.5, 'waist_cm': 72.0, 'hypertension_history': 'no', 'smoking_history': 'no', 'sedentary_minutes_day': 180},
            {'age': 52, 'sex': 'male', 'bmi': 28.4, 'waist_cm': 98.5, 'hypertension_history': 'yes', 'smoking_history': 'no', 'sedentary_minutes_day': 480},
            {'age': 65, 'sex': 'female', 'bmi': 34.2, 'waist_cm': 106.0, 'hypertension_history': 'yes', 'smoking_history': 'yes', 'sedentary_minutes_day': 600},
            {'age': 38, 'sex': 'male', 'bmi': 23.1, 'waist_cm': 84.0, 'hypertension_history': 'no', 'smoking_history': 'yes', 'sedentary_minutes_day': 360},
            {'age': 75, 'sex': 'male', 'bmi': 31.0, 'waist_cm': 102.0, 'hypertension_history': 'yes', 'smoking_history': 'no', 'sedentary_minutes_day': 720},
        ]
        import numpy as np
        for case in test_cases:
            # Predict via adapter
            res = self.adapter.predict(case)

            # Direct prediction using raw models
            import pandas as pd
            df_raw = pd.DataFrame([{
                'age': float(case['age']),
                'sex': 1.0 if case['sex'] == 'male' else 0.0,
                'bmi': float(case['bmi']),
                'hypertension_history': 1.0 if case['hypertension_history'] == 'yes' else 0.0,
                'smoking_history': 1.0 if case['smoking_history'] == 'yes' else 0.0,
                'waist_cm': float(case['waist_cm']),
                'sedentary_minutes_day': float(case['sedentary_minutes_day']),
            }])
            X_direct = self.adapter._preprocessor.transform(df_raw)
            prob_direct = float(self.adapter._gam.predict_mu(X_direct)[0])

            abs_diff = abs(res.screening_probability - prob_direct)
            self.assertLessEqual(abs_diff, 1e-12, f"Parity mismatch {abs_diff} > 1e-12 for case {case}")


class ScreeningInferenceViewIntegrationTests(TestCase):
    """Integration tests for POST /screening/run/ endpoint."""

    def setUp(self):
        self.client = Client()
        self.url = reverse('predictor:run_screening')
        self.valid_payload = {
            'age': 52,
            'sex': 'male',
            'bmi': 28.4,
            'waist_cm': 98.5,
            'hypertension_history': 'yes',
            'smoking_history': 'no',
            'sedentary_minutes_day': 480,
        }

    def test_get_run_screening_redirects_to_new(self):
        """Direct GET request to /screening/run/ redirects to /screening/new/."""
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('predictor:new_screening'))


# ==============================================================================
# PHASE D2.4 TEST SUITE: SCREENING RESULT & IMMUTABLE PERSISTENCE
# ==============================================================================

from .models import ScreeningRecord
import uuid
from decimal import Decimal


class ScreeningRecordModelTests(TestCase):
    """Unit tests for the immutable ScreeningRecord entity."""

    def setUp(self):
        self.record = ScreeningRecord.objects.create(
            age=52,
            sex='male',
            bmi=Decimal('28.4'),
            waist_cm=Decimal('98.5'),
            hypertension_history='yes',
            smoking_history='no',
            sedentary_minutes_day=480,
            screening_probability=0.21609117,
            ai_referral_recommended=True,
            decision_threshold=Decimal('0.1389'),
            model_name="Phase-5 GAM (λ=10.0, Splines=10)",
            model_sha256="204a94ff072ef4f1edecebf5a643738c006bbf010f3817b4bb798d3ea6fef41d",
            preprocessor_sha256="6e56a01993a4a6971eb62c82699c49da6f31a3acec2a1169e07862409f42824d",
            input_schema_version="1.0",
        )

    def test_uuid_primary_key(self):
        """Record must use a UUIDv4 primary key, not a sequential integer."""
        self.assertIsInstance(self.record.id, uuid.UUID)

    def test_all_seven_inputs_persisted_with_semantics(self):
        """All 7 inputs are persisted with clinical semantics, not encoded indices."""
        self.assertEqual(self.record.age, 52)
        self.assertEqual(self.record.sex, 'male')
        self.assertEqual(self.record.bmi, Decimal('28.4'))
        self.assertEqual(self.record.waist_cm, Decimal('98.5'))
        self.assertEqual(self.record.hypertension_history, 'yes')
        self.assertEqual(self.record.smoking_history, 'no')
        self.assertEqual(self.record.sedentary_minutes_day, 480)

    def test_original_ai_output_and_provenance(self):
        """Original AI output and model provenance are stored at full precision."""
        self.assertAlmostEqual(self.record.screening_probability, 0.21609117, places=7)
        self.assertTrue(self.record.ai_referral_recommended)
        self.assertEqual(self.record.decision_threshold, Decimal('0.1389'))
        self.assertEqual(self.record.model_sha256, screening_inference.EXPECTED_GAM_SHA256)
        self.assertEqual(self.record.preprocessor_sha256, screening_inference.EXPECTED_PREPROCESSOR_SHA256)
        self.assertIsNotNone(self.record.created_at)

    def test_absence_of_diagnosis_and_override_fields(self):
        """Model must NOT contain diagnosis or human override fields in Phase D2.4."""
        self.assertFalse(hasattr(self.record, 'diagnosis'))
        self.assertFalse(hasattr(self.record, 'predicted_class'))
        self.assertFalse(hasattr(self.record, 'is_diabetic'))
        self.assertFalse(hasattr(self.record, 'override'))
        self.assertFalse(hasattr(self.record, 'reviewer'))
        self.assertFalse(hasattr(self.record, 'final_decision'))


class ScreeningResultWorkflowTests(TestCase):
    """Integration tests for the Post-Redirect-Get (PRG) workflow and result detail view."""

    def setUp(self):
        self.client = Client()
        self.run_url = reverse('predictor:run_screening')
        self.valid_payload = {
            'age': 52,
            'sex': 'male',
            'bmi': 28.4,
            'waist_cm': 98.5,
            'hypertension_history': 'yes',
            'smoking_history': 'no',
            'sedentary_minutes_day': 480,
            'idempotency_token': uuid.uuid4().hex,
        }

    def test_valid_post_creates_screening_record_and_redirects(self):
        """Valid POST creates exactly one ScreeningRecord and redirects (HTTP 302) to result detail."""
        initial_record_count = ScreeningRecord.objects.count()
        initial_pred_count = Prediction.objects.count()
        initial_override_count = Override.objects.count()

        response = self.client.post(self.run_url, data=self.valid_payload)
        self.assertEqual(response.status_code, 302)

        # Confirm exactly one ScreeningRecord was created
        self.assertEqual(ScreeningRecord.objects.count(), initial_record_count + 1)
        # Confirm ZERO legacy Prediction/Override records were created
        self.assertEqual(Prediction.objects.count(), initial_pred_count)
        self.assertEqual(Override.objects.count(), initial_override_count)

        created_record = ScreeningRecord.objects.latest('created_at')
        expected_url = reverse('predictor:screening_result', kwargs={'screening_id': created_record.id})
        self.assertRedirects(response, expected_url)

    def test_invalid_post_creates_no_record(self):
        """Invalid inputs return form with errors and create zero records."""
        payload = self.valid_payload.copy()
        payload['age'] = 15  # Below supported range

        response = self.client.post(self.run_url, data=payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(ScreeningRecord.objects.count(), 0)

    def test_simulated_inference_failure_creates_no_record(self):
        """Inference failure renders error alert and creates zero records."""
        payload = self.valid_payload.copy()
        payload['_simulate_error'] = '1'

        response = self.client.post(self.run_url, data=payload)
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')
        self.assertIn('Screening Inference Execution Error', content)
        self.assertEqual(ScreeningRecord.objects.count(), 0)

    def test_simulated_persistence_failure_rolls_back_cleanly(self):
        """Persistence failure returns safe user error and creates zero records."""
        payload = self.valid_payload.copy()
        payload['_simulate_db_error'] = '1'

        response = self.client.post(self.run_url, data=payload)
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')
        self.assertIn('The screening result could not be saved', content)
        self.assertEqual(ScreeningRecord.objects.count(), 0)

    def test_result_detail_get_renders_without_rerunning_inference(self):
        """GET to result detail renders stored output and NEVER calls model inference."""
        record = ScreeningRecord.objects.create(
            age=52,
            sex='male',
            bmi=Decimal('28.4'),
            waist_cm=Decimal('98.5'),
            hypertension_history='yes',
            smoking_history='no',
            sedentary_minutes_day=480,
            screening_probability=0.21609117,
            ai_referral_recommended=True,
            decision_threshold=Decimal('0.1389'),
        )

        result_url = reverse('predictor:screening_result', kwargs={'screening_id': record.id})

        # Mock predict_screening to guarantee inference is NOT recomputed
        with mock.patch('predictor.services.screening_inference.predict_screening') as mock_predict:
            response = self.client.get(result_url)
            self.assertEqual(response.status_code, 200)
            mock_predict.assert_not_called()

        content = response.content.decode('utf-8')
        self.assertIn('Stage-1 Screening Result', content)
        self.assertIn('21.6%', content)
        self.assertIn('Elevated screening signal', content)
        self.assertIn('Referral for Stage-2 HbA1c assessment is recommended.', content)
        self.assertIn('Research prototype — not a diagnostic tool.', content)
        self.assertIn('Screening Inputs', content)
        self.assertIn('Research &amp; Provenance Details', content)

    def test_result_detail_invalid_uuid_returns_404(self):
        """Non-existent UUID returns HTTP 404."""
        random_uuid = uuid.uuid4()
        result_url = reverse('predictor:screening_result', kwargs={'screening_id': random_uuid})
        response = self.client.get(result_url)
        self.assertEqual(response.status_code, 404)

    def test_duplicate_submission_protection(self):
        """Duplicate submission with same idempotency token redirects without creating extra records."""
        token = uuid.uuid4().hex
        payload = self.valid_payload.copy()
        payload['idempotency_token'] = token

        # First submission
        res1 = self.client.post(self.run_url, data=payload)
        self.assertEqual(res1.status_code, 302)
        self.assertEqual(ScreeningRecord.objects.count(), 1)
        record1 = ScreeningRecord.objects.get(idempotency_token=token)

        # Second submission with same token (e.g. double click)
        with mock.patch('predictor.services.screening_inference.predict_screening') as mock_predict:
            res2 = self.client.post(self.run_url, data=payload)
            self.assertEqual(res2.status_code, 302)
            # Must NOT call inference again
            mock_predict.assert_not_called()
            # Must NOT create second record
            self.assertEqual(ScreeningRecord.objects.count(), 1)
            # Redirects to existing record
            self.assertRedirects(res2, reverse('predictor:screening_result', kwargs={'screening_id': record1.id}))


class ScreeningResultSemanticsTests(TestCase):
    """Tests verifying strict research-safe language on the result page."""

    def setUp(self):
        self.client = Client()

    def test_elevated_screening_signal_presentation(self):
        """Elevated signal displays restrained attention status and required phrasing."""
        record = ScreeningRecord.objects.create(
            age=52, sex='male', bmi=Decimal('28.4'), waist_cm=Decimal('98.5'),
            hypertension_history='yes', smoking_history='no', sedentary_minutes_day=480,
            screening_probability=0.24731,
            ai_referral_recommended=True,
            decision_threshold=Decimal('0.1389'),
        )
        url = reverse('predictor:screening_result', kwargs={'screening_id': record.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')

        # Status and Recommendation
        self.assertIn('Elevated screening signal', content)
        self.assertIn('Referral for Stage-2 HbA1c assessment is recommended.', content)
        self.assertIn('24.7%', content)
        self.assertIn('Stage-2 HbA1c assessment is recommended for further laboratory evaluation.', content)
        self.assertIn('This is a screening recommendation, not a diagnosis.', content)
        # Must NOT use destructive styling for elevated status
        self.assertNotIn('ui-badge-destructive', content)

    def test_lower_screening_signal_presentation(self):
        """Lower signal displays neutral status and never claims disease absence or normal."""
        record = ScreeningRecord.objects.create(
            age=25, sex='female', bmi=Decimal('19.5'), waist_cm=Decimal('72.0'),
            hypertension_history='no', smoking_history='no', sedentary_minutes_day=180,
            screening_probability=0.02102,
            ai_referral_recommended=False,
            decision_threshold=Decimal('0.1389'),
        )
        url = reverse('predictor:screening_result', kwargs={'screening_id': record.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')

        # Status and Recommendation
        self.assertIn('Lower screening signal', content)
        self.assertIn('The screening model does not recommend referral for Stage-2 HbA1c assessment at the current research operating point.', content)
        self.assertIn('A lower screening signal does not rule out dysglycemia.', content)
        self.assertIn('2.1%', content)

        # Prohibited lower-signal words: must NOT guarantee normality
        self.assertNotIn('disease absent', content)
        self.assertNotIn('negative for diabetes', content)
        self.assertNotIn('normal glucose', content)


# ==============================================================================
# PHASE D2.5 — GAM-NATIVE ADDITIVE EXPLANATION TESTS
# ==============================================================================

from .models import ScreeningExplanation
from .services import screening_explanation, screening_inference


class ScreeningExplanationServiceUnitTests(TestCase):
    """Unit tests verifying mathematical fidelity of GAM-native explanation service."""

    def setUp(self):
        self.elevated_payload = {
            'age': 52,
            'sex': 'male',
            'bmi': Decimal('28.4'),
            'waist_cm': Decimal('98.5'),
            'hypertension_history': 'yes',
            'smoking_history': 'no',
            'sedentary_minutes_day': 480,
        }
        self.lower_payload = {
            'age': 25,
            'sex': 'female',
            'bmi': Decimal('19.5'),
            'waist_cm': Decimal('72.0'),
            'hypertension_history': 'no',
            'smoking_history': 'no',
            'sedentary_minutes_day': 180,
        }

    def test_fidelity_reconstruction_elevated_case(self):
        """Reconstruction error must be strictly <= 1e-10 for elevated case."""
        result = screening_explanation.explain_screening(self.elevated_payload)
        self.assertEqual(result.method, 'gam_native_additive')
        self.assertEqual(result.method_version, '1.0')
        self.assertEqual(result.link_function, 'logit')
        self.assertEqual(len(result.contributions), 7)
        self.assertLessEqual(result.reconstruction_error, 1e-10)

        # Check that sum of terms + intercept equals reconstructed linear predictor
        sum_terms = result.intercept + sum(c.contribution for c in result.contributions)
        self.assertAlmostEqual(sum_terms, result.reconstructed_linear_predictor, places=12)

    def test_fidelity_reconstruction_lower_case(self):
        """Reconstruction error must be strictly <= 1e-10 for lower case."""
        result = screening_explanation.explain_screening(self.lower_payload)
        self.assertEqual(len(result.contributions), 7)
        self.assertLessEqual(result.reconstruction_error, 1e-10)

    def test_contributions_structure_and_formatting(self):
        """Each of the 7 contributions must contain required metadata and formatting."""
        result = screening_explanation.explain_screening(self.elevated_payload)
        feature_names = [c.feature_name for c in result.contributions]
        expected_features = ['age', 'sex', 'bmi', 'waist_cm', 'hypertension_history', 'smoking_history', 'sedentary_minutes_day']
        self.assertEqual(set(feature_names), set(expected_features))

        for c in result.contributions:
            self.assertIn(c.direction, ['higher', 'lower'])
            self.assertGreater(len(c.display_name), 0)
            self.assertGreater(len(c.formatted_value), 0)
            self.assertEqual(c.abs_contribution, abs(c.contribution))


class ScreeningExplanationPersistenceTests(TestCase):
    """Integration tests verifying atomic explanation persistence during screening workflow."""

    def setUp(self):
        self.client = Client()
        self.run_url = reverse('predictor:run_screening')
        self.payload = {
            'age': 52,
            'sex': 'male',
            'bmi': '28.4',
            'waist_cm': '98.5',
            'hypertension_history': 'yes',
            'smoking_history': 'no',
            'sedentary_minutes_day': 480,
            'idempotency_token': 'phase-d2-5-persistence-token-01',
        }

    def test_successful_screening_persists_explanation(self):
        """POST to run_screening atomically creates ScreeningRecord and ScreeningExplanation."""
        res = self.client.post(self.run_url, data=self.payload)
        self.assertEqual(res.status_code, 302)

        record = ScreeningRecord.objects.get(idempotency_token='phase-d2-5-persistence-token-01')
        self.assertTrue(hasattr(record, 'explanation'))
        explanation = record.explanation
        self.assertEqual(explanation.status, 'generated')
        self.assertEqual(explanation.method, 'gam_native_additive')
        self.assertEqual(len(explanation.contributions_json), 7)
        self.assertLessEqual(explanation.reconstruction_error, 1e-10)
        self.assertEqual(explanation.model_sha256, screening_inference.EXPECTED_GAM_SHA256)


class ScreeningExplanationViewTests(TestCase):
    """Tests verifying presentation and zero-recalculation invariant on result detail page."""

    def setUp(self):
        self.client = Client()
        self.record = ScreeningRecord.objects.create(
            age=52, sex='male', bmi=Decimal('28.4'), waist_cm=Decimal('98.5'),
            hypertension_history='yes', smoking_history='no', sedentary_minutes_day=480,
            screening_probability=0.24731,
            ai_referral_recommended=True,
            decision_threshold=Decimal('0.1389'),
        )
        # Create corresponding explanation
        exp_res = screening_explanation.explain_screening({
            'age': 52, 'sex': 'male', 'bmi': Decimal('28.4'), 'waist_cm': Decimal('98.5'),
            'hypertension_history': 'yes', 'smoking_history': 'no', 'sedentary_minutes_day': 480,
        })
        self.explanation = ScreeningExplanation.objects.create(
            screening_record=self.record,
            method=exp_res.method,
            method_version=exp_res.method_version,
            link_function=exp_res.link_function,
            intercept=exp_res.intercept,
            contributions_json=[c.to_dict() for c in exp_res.contributions],
            reconstructed_linear_predictor=exp_res.reconstructed_linear_predictor,
            reconstructed_probability=exp_res.reconstructed_probability,
            reconstruction_error=exp_res.reconstruction_error,
            model_sha256=exp_res.model_sha256,
            status='generated',
        )
        self.url = reverse('predictor:screening_result', kwargs={'screening_id': self.record.id})

    def test_why_this_result_rendered_properly(self):
        """Result page displays Why this result card with non-causal copy and factor items."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')

        self.assertIn('Why this result?', content)
        self.assertIn('GAM-Native Additive v1.0', content)
        self.assertIn('These values represent the mathematical term contributions of the frozen GAM model', content)
        self.assertIn('not biological causation', content)
        self.assertIn('Pushes screening score higher', content)
        self.assertIn('Model Baseline (Intercept', content)
        self.assertIn('Fidelity verified', content)
        self.assertIn('toggle-all-factors-btn', content)

    def test_zero_recalculation_on_get(self):
        """GET to result detail must NEVER rerun inference or explanation services."""
        with mock.patch('predictor.services.screening_inference.predict_screening') as mock_inf:
            with mock.patch('predictor.services.screening_explanation.explain_screening') as mock_exp:
                response = self.client.get(self.url)
                self.assertEqual(response.status_code, 200)
                mock_inf.assert_not_called()
                mock_exp.assert_not_called()


class ScreeningExplanationFailureHandlingTests(TestCase):
    """Tests verifying dignified fallback when explanation computation fails."""

    def setUp(self):
        self.client = Client()
        self.run_url = reverse('predictor:run_screening')

    def test_simulated_explanation_failure_falls_back_gracefully(self):
        """Simulated explanation failure persists failed explanation without aborting ScreeningRecord."""
        payload = {
            'age': 52,
            'sex': 'male',
            'bmi': '28.4',
            'waist_cm': '98.5',
            'hypertension_history': 'yes',
            'smoking_history': 'no',
            'sedentary_minutes_day': 480,
            '_simulate_explanation_error': '1',
            'idempotency_token': 'simulated-explanation-err-token',
        }
        res = self.client.post(self.run_url, data=payload)
        self.assertEqual(res.status_code, 302)

        record = ScreeningRecord.objects.get(idempotency_token='simulated-explanation-err-token')
        self.assertIsNotNone(record)
        self.assertEqual(record.explanation.status, 'failed')
        self.assertIn('Simulated explanation failure', record.explanation.failure_reason)

        # GET to result page displays failure alert without breaking main result
        result_url = reverse('predictor:screening_result', kwargs={'screening_id': record.id})
        res_page = self.client.get(result_url)
        self.assertEqual(res_page.status_code, 200)
        content = res_page.content.decode('utf-8')

        self.assertIn('Model explanation temporarily unavailable', content)
        self.assertIn('The screening result and recommendation above remain fully valid and verified.', content)
        # Main screening result is intact
        self.assertIn('Elevated screening signal', content)
        self.assertIn('Referral for Stage-2 HbA1c assessment is recommended.', content)


class LegacyShapDecouplingTests(TestCase):
    """Tests verifying complete architectural decoupling of Phase-5 Stage-1 from legacy SHAP."""

    def setUp(self):
        self.client = Client()
        self.record = ScreeningRecord.objects.create(
            age=52, sex='male', bmi=Decimal('28.4'), waist_cm=Decimal('98.5'),
            hypertension_history='yes', smoking_history='no', sedentary_minutes_day=480,
            screening_probability=0.24731,
            ai_referral_recommended=True,
            decision_threshold=Decimal('0.1389'),
        )
        exp_res = screening_explanation.explain_screening({
            'age': 52, 'sex': 'male', 'bmi': Decimal('28.4'), 'waist_cm': Decimal('98.5'),
            'hypertension_history': 'yes', 'smoking_history': 'no', 'sedentary_minutes_day': 480,
        })
        self.explanation = ScreeningExplanation.objects.create(
            screening_record=self.record,
            method=exp_res.method,
            method_version=exp_res.method_version,
            link_function=exp_res.link_function,
            intercept=exp_res.intercept,
            contributions_json=[c.to_dict() for c in exp_res.contributions],
            reconstructed_linear_predictor=exp_res.reconstructed_linear_predictor,
            reconstructed_probability=exp_res.reconstructed_probability,
            reconstruction_error=exp_res.reconstruction_error,
            model_sha256=exp_res.model_sha256,
            status='generated',
        )
        self.url = reverse('predictor:screening_result', kwargs={'screening_id': self.record.id})

    def test_no_shap_in_screening_result_page(self):
        """Result page content must not contain legacy SHAP terminology or elements."""
        response = self.client.get(self.url)
        content = response.content.decode('utf-8')
        # SHAP references should not appear in Stage-1 presentation
        self.assertNotIn('SHAP', content)
        self.assertNotIn('shap_values', content)
        self.assertNotIn('shap_explainer', content)

    def test_legacy_shap_explainer_not_invoked_during_stage1_pipeline(self):
        """Executing Stage-1 screening must NEVER invoke legacy shap_explainer."""
        with mock.patch('predictor.shap_explainer.explain_prediction', side_effect=AssertionError("SHAP called!")) if hasattr(screening_inference, 'shap_explainer') else mock.MagicMock():
            payload = {
                'age': 52,
                'sex': 'male',
                'bmi': '28.4',
                'waist_cm': '98.5',
                'hypertension_history': 'yes',
                'smoking_history': 'no',
                'sedentary_minutes_day': 480,
            }
            res = self.client.post(reverse('predictor:run_screening'), data=payload)
            self.assertEqual(res.status_code, 302)


# ==============================================================================
# PHASE D2.6 — HUMAN REVIEW & ACCEPT RECOMMENDATION TESTS
# ==============================================================================

from django.db import IntegrityError
from .models import HumanReview
from .forms import HumanReviewAcceptForm


class HumanReviewModelUnitTests(TestCase):
    """Unit tests verifying HumanReview schema constraints and model invariants."""

    def setUp(self):
        self.record = ScreeningRecord.objects.create(
            age=52, sex='male', bmi=Decimal('28.4'), waist_cm=Decimal('98.5'),
            hypertension_history='yes', smoking_history='no', sedentary_minutes_day=480,
            screening_probability=0.24731,
            ai_referral_recommended=True,
            decision_threshold=Decimal('0.1389'),
        )

    def test_human_review_fields_and_creation(self):
        """HumanReview creates successfully with UUID, reviewer code, and derived decision."""
        review = HumanReview.objects.create(
            screening_record=self.record,
            reviewer_code="R001",
            review_action="accepted",
            final_referral_recommended=True,
        )
        self.assertIsNotNone(review.id)
        self.assertEqual(len(str(review.id)), 36)  # Standard UUID string length
        self.assertEqual(review.reviewer_code, "R001")
        self.assertEqual(review.review_action, "accepted")
        self.assertTrue(review.final_referral_recommended)
        self.assertIsNotNone(review.created_at)
        self.assertEqual(review.action_display, "Recommendation Accepted")
        self.assertEqual(review.final_decision_text, "Refer for Stage-2 HbA1c assessment")

    def test_one_to_one_relation_enforced(self):
        """OneToOneField strictly prevents multiple reviews for the same ScreeningRecord."""
        HumanReview.objects.create(
            screening_record=self.record,
            reviewer_code="R001",
            review_action="accepted",
            final_referral_recommended=True,
        )
        with self.assertRaises(IntegrityError):
            HumanReview.objects.create(
                screening_record=self.record,
                reviewer_code="R002",
                review_action="accepted",
                final_referral_recommended=True,
            )

    def test_forbidden_fields_absent(self):
        """Model must NOT contain diagnosis, HbA1c, or override reason fields in Phase D2.6."""
        field_names = [f.name for f in HumanReview._meta.get_fields()]
        self.assertNotIn('diagnosis', field_names)
        self.assertNotIn('diabetes_status', field_names)
        self.assertNotIn('hba1c', field_names)
        self.assertNotIn('override_reason', field_names)
        self.assertNotIn('notes', field_names)
        self.assertNotIn('doctor_name', field_names)


class HumanReviewAcceptWorkflowTests(TestCase):
    """Integration tests verifying the accept recommendation workflow for REFER and DO NOT REFER."""

    def setUp(self):
        self.client = Client()
        # 1. Elevated record with faithful explanation
        self.elevated_record = ScreeningRecord.objects.create(
            age=52, sex='male', bmi=Decimal('28.4'), waist_cm=Decimal('98.5'),
            hypertension_history='yes', smoking_history='no', sedentary_minutes_day=480,
            screening_probability=0.25608,
            ai_referral_recommended=True,
            decision_threshold=Decimal('0.1389'),
        )
        ScreeningExplanation.objects.create(
            screening_record=self.elevated_record,
            method="gam_native_additive",
            method_version="1.0",
            link_function="logit",
            intercept=-0.7291,
            contributions_json=[],
            reconstructed_linear_predictor=-1.066,
            reconstructed_probability=0.25608,
            reconstruction_error=0.0,
            model_sha256=screening_inference.EXPECTED_GAM_SHA256,
            status='generated',
        )

        # 2. Lower record with faithful explanation
        self.lower_record = ScreeningRecord.objects.create(
            age=25, sex='female', bmi=Decimal('19.5'), waist_cm=Decimal('72.0'),
            hypertension_history='no', smoking_history='no', sedentary_minutes_day=180,
            screening_probability=0.02053,
            ai_referral_recommended=False,
            decision_threshold=Decimal('0.1389'),
        )
        ScreeningExplanation.objects.create(
            screening_record=self.lower_record,
            method="gam_native_additive",
            method_version="1.0",
            link_function="logit",
            intercept=-0.7291,
            contributions_json=[],
            reconstructed_linear_predictor=-3.864,
            reconstructed_probability=0.02053,
            reconstruction_error=0.0,
            model_sha256=screening_inference.EXPECTED_GAM_SHA256,
            status='generated',
        )

    def test_accept_elevated_referral_recommendation(self):
        """Accepting an elevated recommendation sets final decision to True and preserves AI output."""
        url = reverse('predictor:accept_review', kwargs={'screening_id': self.elevated_record.id})
        res = self.client.post(url, data={'reviewer_code': 'REV-01'})
        self.assertEqual(res.status_code, 302)
        self.assertRedirects(res, reverse('predictor:screening_result', kwargs={'screening_id': self.elevated_record.id}))

        review = HumanReview.objects.get(screening_record=self.elevated_record)
        self.assertEqual(review.reviewer_code, 'REV-01')
        self.assertEqual(review.review_action, 'accepted')
        self.assertTrue(review.final_referral_recommended)

        # Invariant: AI original output on ScreeningRecord is unchanged
        self.elevated_record.refresh_from_db()
        self.assertTrue(self.elevated_record.ai_referral_recommended)
        self.assertEqual(self.elevated_record.screening_probability, 0.25608)

        # Result detail view now renders reviewed state
        res_view = self.client.get(reverse('predictor:screening_result', kwargs={'screening_id': self.elevated_record.id}))
        content = res_view.content.decode('utf-8')
        self.assertIn('Recommendation Accepted', content)
        self.assertIn('REV-01', content)
        self.assertIn('Refer for Stage-2 HbA1c assessment', content)
        self.assertNotIn('id="accept-recommendation-btn"', content)

    def test_accept_lower_non_referral_recommendation(self):
        """Accepting a lower recommendation sets final decision to False and preserves AI output."""
        url = reverse('predictor:accept_review', kwargs={'screening_id': self.lower_record.id})
        res = self.client.post(url, data={'reviewer_code': 'HP-99'})
        self.assertEqual(res.status_code, 302)

        review = HumanReview.objects.get(screening_record=self.lower_record)
        self.assertEqual(review.reviewer_code, 'HP-99')
        self.assertEqual(review.review_action, 'accepted')
        self.assertFalse(review.final_referral_recommended)

        # Invariant: AI original output remains unchanged
        self.lower_record.refresh_from_db()
        self.assertFalse(self.lower_record.ai_referral_recommended)

        res_view = self.client.get(reverse('predictor:screening_result', kwargs={'screening_id': self.lower_record.id}))
        content = res_view.content.decode('utf-8')
        self.assertIn('Recommendation Accepted', content)
        self.assertIn('No referral recommended at current operating point', content)


class HumanReviewTamperingDefenseTests(TestCase):
    """Tests verifying server-side decision derivation and resistance to client payload tampering."""

    def setUp(self):
        self.client = Client()
        self.record = ScreeningRecord.objects.create(
            age=52, sex='male', bmi=Decimal('28.4'), waist_cm=Decimal('98.5'),
            hypertension_history='yes', smoking_history='no', sedentary_minutes_day=480,
            screening_probability=0.25608,
            ai_referral_recommended=True,
            decision_threshold=Decimal('0.1389'),
        )
        ScreeningExplanation.objects.create(
            screening_record=self.record,
            method="gam_native_additive",
            method_version="1.0",
            link_function="logit",
            intercept=-0.7291,
            contributions_json=[],
            reconstructed_linear_predictor=-1.066,
            reconstructed_probability=0.25608,
            reconstruction_error=0.0,
            model_sha256=screening_inference.EXPECTED_GAM_SHA256,
            status='generated',
        )

    def test_tampered_payload_cannot_change_final_decision(self):
        """Client POST attempting to submit final_referral_recommended=False is ignored."""
        url = reverse('predictor:accept_review', kwargs={'screening_id': self.record.id})
        malicious_payload = {
            'reviewer_code': 'MAL-01',
            'final_referral_recommended': 'false',
            'ai_referral_recommended': 'false',
            'screening_probability': '0.01',
            'decision_threshold': '0.50',
        }
        res = self.client.post(url, data=malicious_payload)
        self.assertEqual(res.status_code, 302)

        review = HumanReview.objects.get(screening_record=self.record)
        # Server MUST have derived True from stored ScreeningRecord, ignoring client false
        self.assertTrue(review.final_referral_recommended)
        self.record.refresh_from_db()
        self.assertEqual(self.record.screening_probability, 0.25608)
        self.assertTrue(self.record.ai_referral_recommended)


class HumanReviewDuplicateDefenseTests(TestCase):
    """Tests verifying idempotency and defense against repeated review submissions."""

    def setUp(self):
        self.client = Client()
        self.record = ScreeningRecord.objects.create(
            age=52, sex='male', bmi=Decimal('28.4'), waist_cm=Decimal('98.5'),
            hypertension_history='yes', smoking_history='no', sedentary_minutes_day=480,
            screening_probability=0.25608,
            ai_referral_recommended=True,
            decision_threshold=Decimal('0.1389'),
        )
        ScreeningExplanation.objects.create(
            screening_record=self.record,
            method="gam_native_additive",
            method_version="1.0",
            link_function="logit",
            intercept=-0.7291,
            contributions_json=[],
            reconstructed_linear_predictor=-1.066,
            reconstructed_probability=0.25608,
            reconstruction_error=0.0,
            model_sha256=screening_inference.EXPECTED_GAM_SHA256,
            status='generated',
        )
        self.url = reverse('predictor:accept_review', kwargs={'screening_id': self.record.id})

    def test_repeated_submission_does_not_create_duplicate(self):
        """Submitting accept twice results in exactly 1 HumanReview row with unchanged timestamp."""
        res1 = self.client.post(self.url, data={'reviewer_code': 'REV-FIRST'})
        self.assertEqual(res1.status_code, 302)
        self.assertEqual(HumanReview.objects.filter(screening_record=self.record).count(), 1)
        original_review = HumanReview.objects.get(screening_record=self.record)
        original_ts = original_review.created_at

        # Second submission
        res2 = self.client.post(self.url, data={'reviewer_code': 'REV-SECOND'})
        self.assertEqual(res2.status_code, 302)
        self.assertEqual(HumanReview.objects.filter(screening_record=self.record).count(), 1)

        after_review = HumanReview.objects.get(screening_record=self.record)
        self.assertEqual(after_review.reviewer_code, 'REV-FIRST')
        self.assertEqual(after_review.created_at, original_ts)


class HumanReviewExplanationPrerequisiteTests(TestCase):
    """Tests verifying that human review requires a faithful explanation prerequisite."""

    def setUp(self):
        self.client = Client()
        # Record with failed explanation
        self.record = ScreeningRecord.objects.create(
            age=48, sex='female', bmi=Decimal('31.2'), waist_cm=Decimal('92.0'),
            hypertension_history='yes', smoking_history='no', sedentary_minutes_day=520,
            screening_probability=0.1852,
            ai_referral_recommended=True,
            decision_threshold=Decimal('0.1389'),
        )
        ScreeningExplanation.objects.create(
            screening_record=self.record,
            method="gam_native_additive",
            method_version="1.0",
            link_function="logit",
            intercept=0.0,
            contributions_json=[],
            reconstructed_linear_predictor=0.0,
            reconstructed_probability=0.0,
            reconstruction_error=0.0,
            model_sha256=screening_inference.EXPECTED_GAM_SHA256,
            status='failed',
            failure_reason="Simulated explanation error for prerequisite test",
        )
        self.url = reverse('predictor:accept_review', kwargs={'screening_id': self.record.id})

    def test_review_blocked_when_explanation_failed(self):
        """Attempting to accept review when explanation failed is rejected."""
        res = self.client.post(self.url, data={'reviewer_code': 'REV-01'})
        self.assertEqual(res.status_code, 302)
        # Zero reviews created
        self.assertEqual(HumanReview.objects.filter(screening_record=self.record).count(), 0)

        # GET to result page shows review unavailable card
        res_view = self.client.get(reverse('predictor:screening_result', kwargs={'screening_id': self.record.id}))
        content = res_view.content.decode('utf-8')
        self.assertIn('Human review is unavailable because the model explanation for this screening could not be generated.', content)
        self.assertIn('review-unavailable-card', content)
        self.assertNotIn('id="accept-recommendation-btn"', content)


class HumanReviewZeroReinferenceTests(TestCase):
    """Tests proving zero ML inference or XAI calls during human review actions."""

    def setUp(self):
        self.client = Client()
        self.record = ScreeningRecord.objects.create(
            age=52, sex='male', bmi=Decimal('28.4'), waist_cm=Decimal('98.5'),
            hypertension_history='yes', smoking_history='no', sedentary_minutes_day=480,
            screening_probability=0.25608,
            ai_referral_recommended=True,
            decision_threshold=Decimal('0.1389'),
        )
        ScreeningExplanation.objects.create(
            screening_record=self.record,
            method="gam_native_additive",
            method_version="1.0",
            link_function="logit",
            intercept=-0.7291,
            contributions_json=[],
            reconstructed_linear_predictor=-1.066,
            reconstructed_probability=0.25608,
            reconstruction_error=0.0,
            model_sha256=screening_inference.EXPECTED_GAM_SHA256,
            status='generated',
        )

    def test_zero_reinference_during_review_post_and_get(self):
        """POST accept review and subsequent GET result must NEVER call predict_screening or explain_screening."""
        accept_url = reverse('predictor:accept_review', kwargs={'screening_id': self.record.id})
        result_url = reverse('predictor:screening_result', kwargs={'screening_id': self.record.id})

        with mock.patch('predictor.services.screening_inference.predict_screening') as mock_inf:
            with mock.patch('predictor.services.screening_explanation.explain_screening') as mock_exp:
                # 1. POST accept
                res_post = self.client.post(accept_url, data={'reviewer_code': 'REV-AUDIT'})
                self.assertEqual(res_post.status_code, 302)
                mock_inf.assert_not_called()
                mock_exp.assert_not_called()

                # 2. GET reviewed detail
                res_get = self.client.get(result_url)
                self.assertEqual(res_get.status_code, 200)
                mock_inf.assert_not_called()
                mock_exp.assert_not_called()


class HumanReviewReviewerCodeValidationTests(TestCase):
    """Unit and form validation tests for anonymous Reviewer Code."""

    def test_valid_reviewer_codes(self):
        """Alphanumeric, hyphen, and underscore codes up to 32 chars pass."""
        valid_codes = ['R001', 'HP-03', 'CLIN_12', 'reviewer-99', 'A', '12345678901234567890123456789012']
        for code in valid_codes:
            form = HumanReviewAcceptForm(data={'reviewer_code': code})
            self.assertTrue(form.is_valid(), msg=f"Failed for code: {code}")

    def test_invalid_reviewer_codes(self):
        """Empty, whitespace, overly long, or special character codes fail."""
        invalid_codes = [
            ('', 'Enter your reviewer code before submitting this review.'),
            ('   ', 'Enter your reviewer code before submitting this review.'),
            ('R001@hospital', 'Reviewer code may contain only letters, numbers, hyphens, and underscores.'),
            ('<script>alert(1)</script>', 'Reviewer code may contain only letters, numbers, hyphens, and underscores.'),
            ('R 001', 'Reviewer code may contain only letters, numbers, hyphens, and underscores.'),
            ('a' * 33, 'Reviewer code must be 32 characters or fewer.'),
        ]
        for code, expected_error in invalid_codes:
            form = HumanReviewAcceptForm(data={'reviewer_code': code})
            self.assertFalse(form.is_valid(), msg=f"Should be invalid: {code}")
            self.assertIn(expected_error, str(form.errors))


# ==============================================================================
# PHASE D2.7 — HUMAN OVERRIDE WORKFLOW + STRUCTURED RATIONALE TESTS
# ==============================================================================

class HumanOverrideWorkflowTests(TestCase):
    """Core tests for Human Override branch-sensitive workflow and rationale."""

    def setUp(self):
        self.client = Client()
        # Elevated AI recommendation record
        self.elevated_record = ScreeningRecord.objects.create(
            age=55, sex='male', bmi=Decimal('29.4'), waist_cm=Decimal('98.0'),
            hypertension_history='yes', smoking_history='no', sedentary_minutes_day=450,
            screening_probability=0.2241,
            ai_referral_recommended=True,
            decision_threshold=Decimal('0.1389'),
        )
        ScreeningExplanation.objects.create(
            screening_record=self.elevated_record,
            method="gam_native_additive", method_version="1.0", link_function="logit",
            intercept=-0.7291, contributions_json=[],
            reconstructed_linear_predictor=-1.242, reconstructed_probability=0.2241,
            reconstruction_error=0.0, model_sha256=screening_inference.EXPECTED_GAM_SHA256,
            status='generated',
        )

        # Lower AI recommendation record
        self.lower_record = ScreeningRecord.objects.create(
            age=26, sex='female', bmi=Decimal('21.0'), waist_cm=Decimal('74.0'),
            hypertension_history='no', smoking_history='no', sedentary_minutes_day=180,
            screening_probability=0.0315,
            ai_referral_recommended=False,
            decision_threshold=Decimal('0.1389'),
        )
        ScreeningExplanation.objects.create(
            screening_record=self.lower_record,
            method="gam_native_additive", method_version="1.0", link_function="logit",
            intercept=-0.7291, contributions_json=[],
            reconstructed_linear_predictor=-3.425, reconstructed_probability=0.0315,
            reconstruction_error=0.0, model_sha256=screening_inference.EXPECTED_GAM_SHA256,
            status='generated',
        )

    def test_override_refer_to_no_refer(self):
        """Override an elevated REFER signal to DO NOT REFER with valid structured reason."""
        url = reverse('predictor:override_review', kwargs={'screening_id': self.elevated_record.id})
        with mock.patch('predictor.services.screening_inference.predict_screening') as mock_inf:
            with mock.patch('predictor.services.screening_explanation.explain_screening') as mock_exp:
                res = self.client.post(url, data={
                    'reviewer_code': 'REV-01',
                    'override_reason_code': 'additional_context_reduces_concern',
                    'override_note': 'Recent rigorous clinical exam showed normal vitals and active lifestyle.',
                })
                self.assertEqual(res.status_code, 302)
                mock_inf.assert_not_called()
                mock_exp.assert_not_called()

        review = HumanReview.objects.get(screening_record=self.elevated_record)
        self.assertEqual(review.review_action, 'overridden')
        self.assertFalse(review.final_referral_recommended)
        self.assertTrue(self.elevated_record.ai_referral_recommended)  # AI output immutable
        self.assertEqual(review.reviewer_code, 'REV-01')
        self.assertEqual(review.override_reason_code, 'additional_context_reduces_concern')
        self.assertIn('recent rigorous', review.override_note.lower())

    def test_override_no_refer_to_refer(self):
        """Override a lower NO REFER signal to REFER with valid structured reason."""
        url = reverse('predictor:override_review', kwargs={'screening_id': self.lower_record.id})
        with mock.patch('predictor.services.screening_inference.predict_screening') as mock_inf:
            with mock.patch('predictor.services.screening_explanation.explain_screening') as mock_exp:
                res = self.client.post(url, data={
                    'reviewer_code': 'REV-02',
                    'override_reason_code': 'precautionary_referral',
                    'override_note': 'High family risk observed in clinical interview.',
                })
                self.assertEqual(res.status_code, 302)
                mock_inf.assert_not_called()
                mock_exp.assert_not_called()

        review = HumanReview.objects.get(screening_record=self.lower_record)
        self.assertEqual(review.review_action, 'overridden')
        self.assertTrue(review.final_referral_recommended)
        self.assertFalse(self.lower_record.ai_referral_recommended)  # AI output immutable
        self.assertEqual(review.reviewer_code, 'REV-02')
        self.assertEqual(review.override_reason_code, 'precautionary_referral')

    def test_accept_regression(self):
        """Accept workflow from D2.6 remains completely functional."""
        url = reverse('predictor:accept_review', kwargs={'screening_id': self.elevated_record.id})
        res = self.client.post(url, data={'reviewer_code': 'REV-ACCEPT'})
        self.assertEqual(res.status_code, 302)
        review = HumanReview.objects.get(screening_record=self.elevated_record)
        self.assertEqual(review.review_action, 'accepted')
        self.assertTrue(review.final_referral_recommended)
        self.assertIsNone(review.override_reason_code)
        self.assertIsNone(review.override_note)

    def test_invalid_same_decision_at_model_level(self):
        """Model validation rejects an override where final decision equals AI recommendation."""
        review = HumanReview(
            screening_record=self.elevated_record,
            reviewer_code='REV-SAME',
            review_action='overridden',
            final_referral_recommended=True,  # Same as AI recommendation True!
            override_reason_code='additional_context_reduces_concern',
        )
        with self.assertRaises(ValidationError) as cm:
            review.clean()
        self.assertIn('different from AI recommendation', str(cm.exception))

    def test_invalid_reason_branch_rejected(self):
        """Reason codes belonging to opposite branch are rejected."""
        url = reverse('predictor:override_review', kwargs={'screening_id': self.elevated_record.id})
        # 'precautionary_referral' is only valid for NO REFER -> REFER, not REFER -> NO REFER
        res = self.client.post(url, data={
            'reviewer_code': 'REV-01',
            'override_reason_code': 'precautionary_referral',
            'override_note': 'Attempting invalid reason',
        })
        self.assertEqual(res.status_code, 302)
        # Zero reviews created
        self.assertEqual(HumanReview.objects.filter(screening_record=self.elevated_record).count(), 0)

    def test_other_reason_without_note_rejected(self):
        """Selecting 'other' without providing a note is rejected."""
        url = reverse('predictor:override_review', kwargs={'screening_id': self.elevated_record.id})
        res = self.client.post(url, data={
            'reviewer_code': 'REV-01',
            'override_reason_code': 'other',
            'override_note': '   ',  # Empty/whitespace
        })
        self.assertEqual(res.status_code, 302)
        self.assertEqual(HumanReview.objects.filter(screening_record=self.elevated_record).count(), 0)

    def test_other_reason_with_valid_note_accepted(self):
        """Selecting 'other' with a non-empty note succeeds."""
        url = reverse('predictor:override_review', kwargs={'screening_id': self.elevated_record.id})
        res = self.client.post(url, data={
            'reviewer_code': 'REV-01',
            'override_reason_code': 'other',
            'override_note': 'Patient has non-fasting acute glucose spike noted.',
        })
        self.assertEqual(res.status_code, 302)
        review = HumanReview.objects.get(screening_record=self.elevated_record)
        self.assertEqual(review.override_reason_code, 'other')
        self.assertEqual(review.override_note, 'Patient has non-fasting acute glucose spike noted.')

    def test_tampering_payload_ignored(self):
        """Injected client decision flags cannot alter server-derived opposite decision."""
        url = reverse('predictor:override_review', kwargs={'screening_id': self.elevated_record.id})
        res = self.client.post(url, data={
            'reviewer_code': 'REV-TAMPER',
            'override_reason_code': 'additional_context_reduces_concern',
            'final_referral_recommended': 'true',  # Injected maliciously
            'review_action': 'accepted',           # Injected maliciously
            'screening_probability': '0.01',       # Injected maliciously
        })
        self.assertEqual(res.status_code, 302)
        review = HumanReview.objects.get(screening_record=self.elevated_record)
        self.assertEqual(review.review_action, 'overridden')
        self.assertFalse(review.final_referral_recommended)  # Derived server-side as False
        self.assertEqual(self.elevated_record.screening_probability, 0.2241)  # Unmodified

    def test_duplicate_and_concurrency_defense(self):
        """Cannot submit override twice, or accept then override, or override then accept."""
        url_override = reverse('predictor:override_review', kwargs={'screening_id': self.elevated_record.id})
        url_accept = reverse('predictor:accept_review', kwargs={'screening_id': self.elevated_record.id})

        # 1. First valid override
        res1 = self.client.post(url_override, data={
            'reviewer_code': 'REV-FIRST',
            'override_reason_code': 'additional_context_reduces_concern',
        })
        self.assertEqual(res1.status_code, 302)
        self.assertEqual(HumanReview.objects.filter(screening_record=self.elevated_record).count(), 1)
        original_time = HumanReview.objects.get(screening_record=self.elevated_record).created_at

        # 2. Second override attempt blocked
        res2 = self.client.post(url_override, data={
            'reviewer_code': 'REV-SECOND',
            'override_reason_code': 'input_quality_concern',
        })
        self.assertEqual(res2.status_code, 302)
        self.assertEqual(HumanReview.objects.filter(screening_record=self.elevated_record).count(), 1)
        review_after = HumanReview.objects.get(screening_record=self.elevated_record)
        self.assertEqual(review_after.reviewer_code, 'REV-FIRST')
        self.assertEqual(review_after.created_at, original_time)

        # 3. Accept attempt on already-overridden record blocked
        res3 = self.client.post(url_accept, data={'reviewer_code': 'REV-THIRD'})
        self.assertEqual(res3.status_code, 302)
        review_final = HumanReview.objects.get(screening_record=self.elevated_record)
        self.assertEqual(review_final.review_action, 'overridden')
        self.assertEqual(review_final.reviewer_code, 'REV-FIRST')

    def test_override_blocked_when_explanation_failed_or_missing(self):
        """Override is blocked when model explanation is missing or in failed status."""
        record_no_exp = ScreeningRecord.objects.create(
            age=40, sex='female', bmi=Decimal('25.0'), waist_cm=Decimal('80.0'),
            hypertension_history='no', smoking_history='no', sedentary_minutes_day=300,
            screening_probability=0.0812,
            ai_referral_recommended=False,
            decision_threshold=Decimal('0.1389'),
        )
        url = reverse('predictor:override_review', kwargs={'screening_id': record_no_exp.id})
        res = self.client.post(url, data={
            'reviewer_code': 'REV-01',
            'override_reason_code': 'precautionary_referral',
        })
        self.assertEqual(res.status_code, 302)
        self.assertEqual(HumanReview.objects.filter(screening_record=record_no_exp).count(), 0)

    def test_overridden_result_get_renders_all_fields_without_reinference(self):
        """GET request on overridden record renders original AI recommendation, final decision, and reason."""
        # Create finalized override
        review = HumanReview.objects.create(
            screening_record=self.elevated_record,
            reviewer_code='REV-DISPLAY',
            review_action='overridden',
            final_referral_recommended=False,
            override_reason_code='additional_context_reduces_concern',
            override_note='Clinical exam performed by senior researcher.',
        )
        result_url = reverse('predictor:screening_result', kwargs={'screening_id': self.elevated_record.id})

        with mock.patch('predictor.services.screening_inference.predict_screening') as mock_inf:
            with mock.patch('predictor.services.screening_explanation.explain_screening') as mock_exp:
                res = self.client.get(result_url)
                self.assertEqual(res.status_code, 200)
                mock_inf.assert_not_called()
                mock_exp.assert_not_called()

        content = res.content.decode('utf-8')
        self.assertIn('Recommendation Overridden', content)
        self.assertIn('Refer for Stage-2 HbA1c', content)
        self.assertIn('No referral recommended at current operating point', content)
        self.assertIn('Additional context supports not referring at this time', content)
        self.assertIn('Clinical exam performed by senior researcher.', content)
        self.assertIn('REV-DISPLAY', content)
        self.assertNotIn('id="accept-recommendation-btn"', content)
        self.assertNotIn('id="open-override-btn"', content)


# ==============================================================================
# PHASE D2.8 — STAGE-2 HbA1c LABORATORY ASSESSMENT & CASCADE COMPLETION TESTS
# ==============================================================================

from .models import Stage2Assessment
from .services.hba1c_range import (
    classify_hba1c_range, HbA1cValidationError, RANGE_RULE_VERSION,
    NORMAL_THRESHOLD, DIABETES_THRESHOLD, MIN_SAFE_HBA1C, MAX_SAFE_HBA1C,
)


class HbA1cRangeServiceUnitTests(TestCase):
    """
    Unit tests for deterministic Stage-2 HbA1c classification service.
    Verifies ADA 2026 boundary conditions, Decimal arithmetic precision, and domain safety.
    """

    def test_normal_range_boundary(self):
        """Values below 5.7% are categorized as Normal-range."""
        # 5.69% boundary test
        res_569 = classify_hba1c_range(Decimal("5.69"))
        self.assertEqual(res_569.range_code, "normal_range")
        self.assertEqual(res_569.range_label, "Normal-range")
        self.assertEqual(res_569.rule_version, RANGE_RULE_VERSION)
        self.assertIn("falls below the 5.7%", res_569.interpretation_copy)

        # 5.20% representative value
        res_520 = classify_hba1c_range(Decimal("5.20"))
        self.assertEqual(res_520.range_code, "normal_range")

    def test_prediabetes_range_boundaries(self):
        """Values between 5.70% and 6.49% inclusive are categorized as Prediabetes-range."""
        # Exact 5.70% boundary
        res_570 = classify_hba1c_range(Decimal("5.70"))
        self.assertEqual(res_570.range_code, "prediabetes_range")
        self.assertEqual(res_570.range_label, "Prediabetes-range")
        self.assertIn("5.7% to <6.5%", res_570.interpretation_copy)

        # Exact 5.7 Decimal representation
        res_57 = classify_hba1c_range(Decimal("5.7"))
        self.assertEqual(res_57.range_code, "prediabetes_range")

        # 6.49% upper prediabetes boundary
        res_649 = classify_hba1c_range(Decimal("6.49"))
        self.assertEqual(res_649.range_code, "prediabetes_range")

    def test_diabetes_range_boundaries(self):
        """Values 6.50% and above are categorized as Diabetes-range."""
        # Exact 6.50% boundary
        res_650 = classify_hba1c_range(Decimal("6.50"))
        self.assertEqual(res_650.range_code, "diabetes_range")
        self.assertEqual(res_650.range_label, "Diabetes-range")
        self.assertIn("≥6.5% laboratory range", res_650.interpretation_copy)

        # Exact 6.5 Decimal representation
        res_65 = classify_hba1c_range(Decimal("6.5"))
        self.assertEqual(res_65.range_code, "diabetes_range")

        # Higher values
        res_820 = classify_hba1c_range(Decimal("8.20"))
        self.assertEqual(res_820.range_code, "diabetes_range")
        res_1150 = classify_hba1c_range(Decimal("11.50"))
        self.assertEqual(res_1150.range_code, "diabetes_range")

    def test_float_input_prohibited(self):
        """Float values are rejected to prevent floating-point representation errors."""
        with self.assertRaises(HbA1cValidationError):
            classify_hba1c_range(5.7)

    def test_negative_and_zero_prohibited(self):
        """Negative and zero values must be rejected."""
        with self.assertRaises(HbA1cValidationError):
            classify_hba1c_range(Decimal("-1.0"))
        with self.assertRaises(HbA1cValidationError):
            classify_hba1c_range(Decimal("0.0"))

    def test_out_of_safety_bounds_prohibited(self):
        """Values outside mathematical/practical safety bounds (2.0 to 25.0) are rejected."""
        with self.assertRaises(HbA1cValidationError):
            classify_hba1c_range(Decimal("1.99"))
        with self.assertRaises(HbA1cValidationError):
            classify_hba1c_range(Decimal("25.01"))

    def test_non_numeric_and_nan_prohibited(self):
        """Invalid strings, NaN, and infinity values are rejected."""
        with self.assertRaises(HbA1cValidationError):
            classify_hba1c_range("invalid")
        with self.assertRaises(HbA1cValidationError):
            classify_hba1c_range(Decimal("NaN"))
        with self.assertRaises(HbA1cValidationError):
            classify_hba1c_range(Decimal("Infinity"))

    def test_rule_version_is_ada_2026(self):
        """Rule version must be stamped as ADA_2026_A1C_RANGE_V1."""
        res = classify_hba1c_range(Decimal("6.00"))
        self.assertEqual(res.rule_version, "ADA_2026_A1C_RANGE_V1")
        self.assertIn("not an automated diagnosis", res.diagnostic_caveat)


class Stage2AssessmentModelUnitTests(TestCase):
    """Unit tests verifying Stage2Assessment schema constraints and domain invariants."""

    def setUp(self):
        self.record = ScreeningRecord.objects.create(
            age=55, sex='female', bmi=Decimal('31.2'), waist_cm=Decimal('99.0'),
            hypertension_history='yes', smoking_history='no', sedentary_minutes_day=420,
            screening_probability=0.2845,
            ai_referral_recommended=True,
            decision_threshold=Decimal('0.1389'),
        )
        self.human_review = HumanReview.objects.create(
            screening_record=self.record,
            reviewer_code="R-MODEL-01",
            review_action="accepted",
            final_referral_recommended=True,
        )

    def test_stage2_creation_success(self):
        """Stage2Assessment creates cleanly with UUID, Decimal HbA1c, and server range."""
        assessment = Stage2Assessment.objects.create(
            human_review=self.human_review,
            hba1c_percent=Decimal("6.20"),
            laboratory_range="prediabetes_range",
            range_rule_version="ADA_2026_A1C_RANGE_V1",
            entry_method="manual",
        )
        self.assertIsNotNone(assessment.id)
        self.assertEqual(assessment.range_display, "Prediabetes-range")
        self.assertIn("5.7% to <6.5%", assessment.interpretation_copy)
        self.assertIn("not an automated diagnosis", assessment.diagnostic_caveat)

    def test_one_to_one_relation_enforced(self):
        """Cannot attach two Stage2Assessments to the same HumanReview."""
        Stage2Assessment.objects.create(
            human_review=self.human_review,
            hba1c_percent=Decimal("6.20"),
            laboratory_range="prediabetes_range",
        )
        with self.assertRaises(IntegrityError):
            Stage2Assessment.objects.create(
                human_review=self.human_review,
                hba1c_percent=Decimal("7.10"),
                laboratory_range="diabetes_range",
            )

    def test_prohibited_fields_absent(self):
        """Model must NOT contain diagnosis, confirmed_diabetes, or AI probability fields."""
        fields = [f.name for f in Stage2Assessment._meta.get_fields()]
        self.assertNotIn('diagnosis', fields)
        self.assertNotIn('diabetes_status', fields)
        self.assertNotIn('confirmed_diabetes', fields)
        self.assertNotIn('disease_truth', fields)
        self.assertNotIn('AI_stage2_probability', fields)
        self.assertNotIn('second_model_prediction', fields)

    def test_clean_rejects_non_referred_review(self):
        """clean() raises ValidationError if human review final decision is False."""
        no_refer_record = ScreeningRecord.objects.create(
            age=30, sex='male', bmi=Decimal('22.0'), waist_cm=Decimal('78.0'),
            hypertension_history='no', smoking_history='no', sedentary_minutes_day=200,
            screening_probability=0.0410,
            ai_referral_recommended=False,
            decision_threshold=Decimal('0.1389'),
        )
        no_refer_review = HumanReview.objects.create(
            screening_record=no_refer_record,
            reviewer_code="R-NO-REFER",
            review_action="accepted",
            final_referral_recommended=False,
        )
        assessment = Stage2Assessment(
            human_review=no_refer_review,
            hba1c_percent=Decimal("5.80"),
            laboratory_range="prediabetes_range",
        )
        with self.assertRaises(ValidationError) as ctx:
            assessment.clean()
        self.assertIn("cannot be created for a screening review where final referral was not recommended", str(ctx.exception))

    def test_clean_rejects_tampered_range(self):
        """clean() raises ValidationError if laboratory_range does not match server classification."""
        assessment = Stage2Assessment(
            human_review=self.human_review,
            hba1c_percent=Decimal("8.50"),  # Should be diabetes_range
            laboratory_range="normal_range",  # Spoofed
        )
        with self.assertRaises(ValidationError) as ctx:
            assessment.clean()
        self.assertIn("Laboratory range mismatch", str(ctx.exception))


class Stage2EligibilityMatrixIntegrationTests(TestCase):
    """
    Integration tests covering the complete four-branch eligibility matrix.
    Stage 2 must only be accessible when final human referral is True.
    """

    def setUp(self):
        # AI REFER record
        self.rec_ai_refer = ScreeningRecord.objects.create(
            age=62, sex='male', bmi=Decimal('29.5'), waist_cm=Decimal('102.0'),
            hypertension_history='yes', smoking_history='yes', sedentary_minutes_day=600,
            screening_probability=0.3412,
            ai_referral_recommended=True,
            decision_threshold=Decimal('0.1389'),
        )
        ScreeningExplanation.objects.create(
            screening_record=self.rec_ai_refer,
            method="gam_native_additive", method_version="1.0", link_function="logit",
            intercept=-0.7291, contributions_json=[], reconstructed_linear_predictor=-0.657,
            reconstructed_probability=0.3412, reconstruction_error=0.0,
            model_sha256="204a94ff072ef4f1edecebf5a643738c006bbf010f3817b4bb798d3ea6fef41d",
            status='generated',
        )

        # AI NO REFER record
        self.rec_ai_no_refer = ScreeningRecord.objects.create(
            age=26, sex='female', bmi=Decimal('21.0'), waist_cm=Decimal('74.0'),
            hypertension_history='no', smoking_history='no', sedentary_minutes_day=150,
            screening_probability=0.0350,
            ai_referral_recommended=False,
            decision_threshold=Decimal('0.1389'),
        )
        ScreeningExplanation.objects.create(
            screening_record=self.rec_ai_no_refer,
            method="gam_native_additive", method_version="1.0", link_function="logit",
            intercept=-0.7291, contributions_json=[], reconstructed_linear_predictor=-3.317,
            reconstructed_probability=0.0350, reconstruction_error=0.0,
            model_sha256="204a94ff072ef4f1edecebf5a643738c006bbf010f3817b4bb798d3ea6fef41d",
            status='generated',
        )

    def test_case_a_ai_refer_accept_refer_allows_stage2(self):
        """Case A: AI Refer + Human Accept = Final Refer -> Stage 2 allowed."""
        HumanReview.objects.create(
            screening_record=self.rec_ai_refer,
            reviewer_code="REV-A",
            review_action="accepted",
            final_referral_recommended=True,
        )
        url = reverse('predictor:stage2', kwargs={'screening_id': self.rec_ai_refer.id})
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        self.assertIn('Stage 2 · HbA1c Laboratory Assessment', res.content.decode('utf-8'))
        self.assertIn('id="hba1c-input"', res.content.decode('utf-8'))

    def test_case_b_ai_no_refer_override_refer_allows_stage2(self):
        """Case B: AI No-Refer + Human Override = Final Refer -> Stage 2 allowed."""
        HumanReview.objects.create(
            screening_record=self.rec_ai_no_refer,
            reviewer_code="REV-B",
            review_action="overridden",
            final_referral_recommended=True,
            override_reason_code="additional_context_increases_concern",
        )
        url = reverse('predictor:stage2', kwargs={'screening_id': self.rec_ai_no_refer.id})
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        self.assertIn('Stage 2 · HbA1c Laboratory Assessment', res.content.decode('utf-8'))
        self.assertIn('id="hba1c-input"', res.content.decode('utf-8'))

    def test_case_c_ai_refer_override_no_refer_blocks_stage2(self):
        """Case C: AI Refer + Human Override = Final No-Refer -> Stage 2 blocked."""
        HumanReview.objects.create(
            screening_record=self.rec_ai_refer,
            reviewer_code="REV-C",
            review_action="overridden",
            final_referral_recommended=False,
            override_reason_code="additional_context_reduces_concern",
        )
        url = reverse('predictor:stage2', kwargs={'screening_id': self.rec_ai_refer.id})
        res = self.client.get(url)
        self.assertEqual(res.status_code, 302)  # Redirects to screening_result
        self.assertEqual(res.url, reverse('predictor:screening_result', kwargs={'screening_id': self.rec_ai_refer.id}))

        # Confirm POST also blocked
        confirm_url = reverse('predictor:stage2_confirm', kwargs={'screening_id': self.rec_ai_refer.id})
        confirm_res = self.client.post(confirm_url, data={'hba1c_percent': '6.10'})
        self.assertEqual(confirm_res.status_code, 302)
        self.assertEqual(Stage2Assessment.objects.filter(human_review__screening_record=self.rec_ai_refer).count(), 0)

    def test_case_d_ai_no_refer_accept_no_refer_blocks_stage2(self):
        """Case D: AI No-Refer + Human Accept = Final No-Refer -> Stage 2 blocked."""
        HumanReview.objects.create(
            screening_record=self.rec_ai_no_refer,
            reviewer_code="REV-D",
            review_action="accepted",
            final_referral_recommended=False,
        )
        url = reverse('predictor:stage2', kwargs={'screening_id': self.rec_ai_no_refer.id})
        res = self.client.get(url)
        self.assertEqual(res.status_code, 302)
        self.assertEqual(res.url, reverse('predictor:screening_result', kwargs={'screening_id': self.rec_ai_no_refer.id}))

    def test_case_e_missing_human_review_blocks_stage2(self):
        """Case E: ScreeningRecord without HumanReview -> Stage 2 blocked."""
        url = reverse('predictor:stage2', kwargs={'screening_id': self.rec_ai_refer.id})
        res = self.client.get(url)
        self.assertEqual(res.status_code, 302)
        self.assertEqual(res.url, reverse('predictor:screening_result', kwargs={'screening_id': self.rec_ai_refer.id}))

    def test_case_f_missing_or_failed_explanation_blocks_stage2(self):
        """Case F: Explanation failure/missing -> Stage 2 blocked."""
        rec_failed_exp = ScreeningRecord.objects.create(
            age=45, sex='male', bmi=Decimal('27.0'), waist_cm=Decimal('90.0'),
            hypertension_history='no', smoking_history='no', sedentary_minutes_day=300,
            screening_probability=0.1500,
            ai_referral_recommended=True,
            decision_threshold=Decimal('0.1389'),
        )
        ScreeningExplanation.objects.create(
            screening_record=rec_failed_exp,
            method="gam_native_additive", method_version="1.0", link_function="logit",
            intercept=-0.7291, contributions_json=[], reconstructed_linear_predictor=0.0,
            reconstructed_probability=0.0, reconstruction_error=0.0,
            model_sha256="fake",
            status='failed', failure_reason="Simulated failure",
        )
        url = reverse('predictor:stage2', kwargs={'screening_id': rec_failed_exp.id})
        res = self.client.get(url)
        self.assertEqual(res.status_code, 302)


class Stage2WorkflowAndPersistenceIntegrationTests(TestCase):
    """
    Tests the complete user journey:
    Enter Value -> Server Validation -> Review HbA1c Value -> Confirm -> Persist -> Result GET.
    """

    def setUp(self):
        self.record = ScreeningRecord.objects.create(
            age=58, sex='male', bmi=Decimal('30.5'), waist_cm=Decimal('101.0'),
            hypertension_history='yes', smoking_history='no', sedentary_minutes_day=450,
            screening_probability=0.2980,
            ai_referral_recommended=True,
            decision_threshold=Decimal('0.1389'),
        )
        ScreeningExplanation.objects.create(
            screening_record=self.record,
            method="gam_native_additive", method_version="1.0", link_function="logit",
            intercept=-0.7291, contributions_json=[], reconstructed_linear_predictor=-0.856,
            reconstructed_probability=0.2980, reconstruction_error=0.0,
            model_sha256="204a94ff072ef4f1edecebf5a643738c006bbf010f3817b4bb798d3ea6fef41d",
            status='generated',
        )
        self.human_review = HumanReview.objects.create(
            screening_record=self.record,
            reviewer_code="REV-FLOW-01",
            review_action="accepted",
            final_referral_recommended=True,
        )

    def test_two_step_review_and_confirmation_flow(self):
        """User enters HbA1c -> views review state -> confirms -> result is persisted."""
        stage2_url = reverse('predictor:stage2', kwargs={'screening_id': self.record.id})
        confirm_url = reverse('predictor:stage2_confirm', kwargs={'screening_id': self.record.id})

        # 1. GET initial entry form
        res_get = self.client.get(stage2_url)
        self.assertEqual(res_get.status_code, 200)
        self.assertIn('id="stage2-entry-form"', res_get.content.decode('utf-8'))

        # 2. POST initial value (Input Review State)
        res_post_entry = self.client.post(stage2_url, data={'hba1c_percent': '6.10'})
        self.assertEqual(res_post_entry.status_code, 200)
        content_review = res_post_entry.content.decode('utf-8')
        self.assertIn('Review Stage-2 Laboratory Measurement', content_review)
        self.assertIn('6.10', content_review)
        self.assertIn('Prediabetes-range', content_review)
        self.assertIn('id="edit-hba1c-btn"', content_review)
        self.assertIn('id="confirm-stage2-btn"', content_review)

        # Database must NOT have persisted Stage2Assessment yet!
        self.assertEqual(Stage2Assessment.objects.filter(human_review=self.human_review).count(), 0)

        # 3. POST confirm to persist
        res_confirm = self.client.post(confirm_url, data={'hba1c_percent': '6.10'})
        self.assertEqual(res_confirm.status_code, 302)
        self.assertEqual(res_confirm.url, stage2_url)

        # Database now has exactly 1 Stage2Assessment
        self.assertEqual(Stage2Assessment.objects.filter(human_review=self.human_review).count(), 1)
        assessment = Stage2Assessment.objects.get(human_review=self.human_review)
        self.assertEqual(assessment.hba1c_percent, Decimal('6.10'))
        self.assertEqual(assessment.laboratory_range, 'prediabetes_range')
        self.assertEqual(assessment.range_rule_version, 'ADA_2026_A1C_RANGE_V1')

        # 4. GET completed result page
        res_result = self.client.get(stage2_url)
        self.assertEqual(res_result.status_code, 200)
        content_res = res_result.content.decode('utf-8')
        self.assertIn('Stage 2 · HbA1c Laboratory Assessment', content_res)
        self.assertIn('6.10', content_res)
        self.assertIn('Prediabetes-range', content_res)
        self.assertIn('ADA Standards of Care in Diabetes — 2026', content_res)
        self.assertIn('Diagnostic Confirmation Notice', content_res)
        self.assertIn('Two-Stage Cascade Lineage', content_res)

        # Verify editing/modifying controls are NOT present on completed result
        self.assertNotIn('id="stage2-entry-form"', content_res)
        self.assertNotIn('id="confirm-stage2-btn"', content_res)

    def test_anti_tampering_payloads_ignored(self):
        """Injected client fields (range, version, diagnosis) are ignored/rejected."""
        confirm_url = reverse('predictor:stage2_confirm', kwargs={'screening_id': self.record.id})
        res = self.client.post(confirm_url, data={
            'hba1c_percent': '8.20',
            'laboratory_range': 'normal_range',       # Injected spoof
            'range_rule_version': 'SPOOFED_VERSION',  # Injected spoof
            'diagnosis': 'diabetes',                  # Injected forbidden field
            'confirmed_diabetes': 'true',             # Injected forbidden field
        })
        self.assertEqual(res.status_code, 302)
        assessment = Stage2Assessment.objects.get(human_review=self.human_review)
        # Server must have derived diabetes_range and frozen ADA 2026 rule version!
        self.assertEqual(assessment.laboratory_range, 'diabetes_range')
        self.assertEqual(assessment.range_rule_version, 'ADA_2026_A1C_RANGE_V1')
        self.assertFalse(hasattr(assessment, 'diagnosis'))

    def test_duplicate_submission_protection(self):
        """Double submitting confirmation does not create duplicate Stage2Assessment records."""
        confirm_url = reverse('predictor:stage2_confirm', kwargs={'screening_id': self.record.id})

        # First submission
        res1 = self.client.post(confirm_url, data={'hba1c_percent': '5.50'})
        self.assertEqual(res1.status_code, 302)
        self.assertEqual(Stage2Assessment.objects.filter(human_review=self.human_review).count(), 1)
        original_created_at = Stage2Assessment.objects.get(human_review=self.human_review).created_at

        # Second submission
        res2 = self.client.post(confirm_url, data={'hba1c_percent': '7.20'})
        self.assertEqual(res2.status_code, 302)
        self.assertEqual(Stage2Assessment.objects.filter(human_review=self.human_review).count(), 1)
        assessment = Stage2Assessment.objects.get(human_review=self.human_review)
        self.assertEqual(assessment.hba1c_percent, Decimal('5.50'))  # Unchanged!
        self.assertEqual(assessment.created_at, original_created_at)

    def test_immutability_of_prior_stages(self):
        """ScreeningRecord and HumanReview remain byte/field identical after Stage 2 creation."""
        # Baseline snapshots
        orig_prob = self.record.screening_probability
        orig_ai_rec = self.record.ai_referral_recommended
        orig_thresh = self.record.decision_threshold
        orig_rev_action = self.human_review.review_action
        orig_final_rec = self.human_review.final_referral_recommended
        orig_rev_code = self.human_review.reviewer_code

        # Create Stage2
        confirm_url = reverse('predictor:stage2_confirm', kwargs={'screening_id': self.record.id})
        self.client.post(confirm_url, data={'hba1c_percent': '6.40'})

        # Refresh from database
        self.record.refresh_from_db()
        self.human_review.refresh_from_db()

        self.assertEqual(self.record.screening_probability, orig_prob)
        self.assertEqual(self.record.ai_referral_recommended, orig_ai_rec)
        self.assertEqual(self.record.decision_threshold, orig_thresh)
        self.assertEqual(self.human_review.review_action, orig_rev_action)
        self.assertEqual(self.human_review.final_referral_recommended, orig_final_rec)
        self.assertEqual(self.human_review.reviewer_code, orig_rev_code)

    def test_zero_ml_and_xai_during_stage2(self):
        """Zero GAM inference or XAI calls occur during Stage-2 entry, review, confirm, or result."""
        stage2_url = reverse('predictor:stage2', kwargs={'screening_id': self.record.id})
        confirm_url = reverse('predictor:stage2_confirm', kwargs={'screening_id': self.record.id})

        with mock.patch('predictor.services.screening_inference.predict_screening') as mock_inf:
            with mock.patch('predictor.services.screening_explanation.explain_screening') as mock_exp:
                # 1. GET entry
                self.client.get(stage2_url)
                # 2. POST review
                self.client.post(stage2_url, data={'hba1c_percent': '6.20'})
                # 3. POST confirm
                self.client.post(confirm_url, data={'hba1c_percent': '6.20'})
                # 4. GET result
                self.client.get(stage2_url)

                mock_inf.assert_not_called()
                mock_exp.assert_not_called()


# ==============================================================================
# PHASE D2.9 — CASE LIFECYCLE, REVIEW QUEUE & SCREENING HISTORY TESTS
# ==============================================================================

from .services.screening_lifecycle import (
    derive_screening_lifecycle,
    audit_record_integrity,
    STATE_EXPLANATION_UNAVAILABLE,
    STATE_PENDING_REVIEW,
    STATE_REVIEWED_NO_REFERRAL,
    STATE_PENDING_STAGE2,
    STATE_COMPLETED_STAGE2,
    STATE_INTEGRITY_ERROR,
    STAGE2_NOT_APPLICABLE,
    STAGE2_PENDING,
    STAGE2_COMPLETED,
    STAGE2_UNAVAILABLE,
)


class ScreeningLifecycleServiceUnitTests(TestCase):
    """Unit tests verifying deterministic lifecycle state derivation and precedence hierarchy."""

    def setUp(self):
        # Base record 1: AI Refer
        self.record_refer = ScreeningRecord.objects.create(
            age=55, sex='male', bmi=Decimal('29.1'), waist_cm=Decimal('101.2'),
            hypertension_history='yes', smoking_history='no', sedentary_minutes_day=450,
            screening_probability=0.254,
            ai_referral_recommended=True,
            decision_threshold=Decimal('0.1389'),
        )
        # Base record 2: AI No Refer
        self.record_no_refer = ScreeningRecord.objects.create(
            age=32, sex='female', bmi=Decimal('22.0'), waist_cm=Decimal('74.5'),
            hypertension_history='no', smoking_history='no', sedentary_minutes_day=240,
            screening_probability=0.045,
            ai_referral_recommended=False,
            decision_threshold=Decimal('0.1389'),
        )

    def _create_explanation(self, record, status='generated'):
        return ScreeningExplanation.objects.create(
            screening_record=record,
            method="gam_native_additive",
            intercept=-2.365,
            contributions_json=[],
            reconstructed_linear_predictor=-1.077,
            reconstructed_probability=0.254,
            reconstruction_error=0.0001,
            status=status,
        )

    def test_state_1_explanation_unavailable_when_missing(self):
        """ScreeningRecord without explanation derives explanation_unavailable."""
        state = derive_screening_lifecycle(self.record_refer)
        self.assertEqual(state.code, STATE_EXPLANATION_UNAVAILABLE)
        self.assertFalse(state.actionable)
        self.assertEqual(state.action_type, "system_attention")
        self.assertEqual(state.stage2_status_code, STAGE2_UNAVAILABLE)

    def test_state_1b_explanation_unavailable_when_failed(self):
        """ScreeningRecord with failed explanation derives explanation_unavailable."""
        self._create_explanation(self.record_refer, status='failed')
        state = derive_screening_lifecycle(self.record_refer)
        self.assertEqual(state.code, STATE_EXPLANATION_UNAVAILABLE)
        self.assertFalse(state.actionable)
        self.assertEqual(state.action_type, "system_attention")

    def test_state_2_pending_review(self):
        """ScreeningRecord with faithful explanation and no HumanReview derives pending_review."""
        self._create_explanation(self.record_refer, status='generated')
        state = derive_screening_lifecycle(self.record_refer)
        self.assertEqual(state.code, STATE_PENDING_REVIEW)
        self.assertTrue(state.actionable)
        self.assertEqual(state.action_type, "review")
        self.assertEqual(state.stage2_status_code, STAGE2_UNAVAILABLE)

    def test_state_3_accepted_final_no_refer(self):
        """Accepted review with AI No Refer derives reviewed_no_referral with stage2 not_applicable."""
        self._create_explanation(self.record_no_refer, status='generated')
        HumanReview.objects.create(
            screening_record=self.record_no_refer,
            reviewer_code="R001",
            review_action="accepted",
            final_referral_recommended=False,
        )
        state = derive_screening_lifecycle(self.record_no_refer)
        self.assertEqual(state.code, STATE_REVIEWED_NO_REFERRAL)
        self.assertFalse(state.actionable)
        self.assertEqual(state.stage2_status_code, STAGE2_NOT_APPLICABLE)
        self.assertEqual(state.stage2_status_label, "Not applicable")

    def test_state_4_overridden_final_no_refer(self):
        """Overridden review from AI Refer to final No Refer derives reviewed_no_referral with stage2 not_applicable."""
        self._create_explanation(self.record_refer, status='generated')
        HumanReview.objects.create(
            screening_record=self.record_refer,
            reviewer_code="R002",
            review_action="overridden",
            final_referral_recommended=False,
            override_reason_code="additional_context_reduces_concern",
        )
        state = derive_screening_lifecycle(self.record_refer)
        self.assertEqual(state.code, STATE_REVIEWED_NO_REFERRAL)
        self.assertFalse(state.actionable)
        self.assertEqual(state.stage2_status_code, STAGE2_NOT_APPLICABLE)
        self.assertEqual(state.stage2_status_label, "Not applicable")

    def test_state_5_accepted_final_refer_no_stage2(self):
        """Accepted review with AI Refer and no Stage 2 derives pending_stage2."""
        self._create_explanation(self.record_refer, status='generated')
        HumanReview.objects.create(
            screening_record=self.record_refer,
            reviewer_code="R003",
            review_action="accepted",
            final_referral_recommended=True,
        )
        state = derive_screening_lifecycle(self.record_refer)
        self.assertEqual(state.code, STATE_PENDING_STAGE2)
        self.assertTrue(state.actionable)
        self.assertEqual(state.action_type, "stage2")
        self.assertEqual(state.stage2_status_code, STAGE2_PENDING)
        self.assertEqual(state.stage2_status_label, "Pending")

    def test_state_6_overridden_final_refer_no_stage2(self):
        """Overridden review from AI No Refer to final Refer and no Stage 2 derives pending_stage2."""
        self._create_explanation(self.record_no_refer, status='generated')
        HumanReview.objects.create(
            screening_record=self.record_no_refer,
            reviewer_code="R004",
            review_action="overridden",
            final_referral_recommended=True,
            override_reason_code="additional_context_increases_concern",
        )
        state = derive_screening_lifecycle(self.record_no_refer)
        self.assertEqual(state.code, STATE_PENDING_STAGE2)
        self.assertTrue(state.actionable)
        self.assertEqual(state.action_type, "stage2")
        self.assertEqual(state.stage2_status_code, STAGE2_PENDING)

    def test_state_7_completed_stage2(self):
        """Final Refer review with Stage2Assessment derives completed_stage2."""
        self._create_explanation(self.record_refer, status='generated')
        review = HumanReview.objects.create(
            screening_record=self.record_refer,
            reviewer_code="R005",
            review_action="accepted",
            final_referral_recommended=True,
        )
        Stage2Assessment.objects.create(
            human_review=review,
            hba1c_percent=Decimal('6.50'),
            laboratory_range='diabetes_range',
            range_rule_version='ADA_2026_A1C_RANGE_V1',
            entry_method='manual',
        )
        state = derive_screening_lifecycle(self.record_refer)
        self.assertEqual(state.code, STATE_COMPLETED_STAGE2)
        self.assertFalse(state.actionable)
        self.assertEqual(state.stage2_status_code, STAGE2_COMPLETED)
        self.assertEqual(state.stage2_status_label, "Completed")

    def test_impossible_state_detection(self):
        """Inconsistent or impossible state combinations are detected as data integrity issues."""
        self._create_explanation(self.record_refer, status='generated')
        review = HumanReview.objects.create(
            screening_record=self.record_refer,
            reviewer_code="R006",
            review_action="accepted",
            final_referral_recommended=True,
        )
        # Directly modify review to create conflict: accepted but decision differs from AI
        HumanReview.objects.filter(id=review.id).update(final_referral_recommended=False)
        self.record_refer.refresh_from_db()

        issues = audit_record_integrity(self.record_refer)
        self.assertTrue(len(issues) > 0)

        state = derive_screening_lifecycle(self.record_refer)
        self.assertEqual(state.code, STATE_INTEGRITY_ERROR)
        self.assertFalse(state.actionable)


class ReviewQueueIntegrationTests(TestCase):
    """Integration tests verifying Review Queue inclusions, exclusions, and read-only behavior."""

    def setUp(self):
        self.client = Client()
        self.url = reverse('predictor:review_queue')

        # Case 1: Pending Human Review (Elevated, generated XAI, no review)
        self.rec1 = ScreeningRecord.objects.create(
            age=50, sex='male', bmi=Decimal('28.0'), waist_cm=Decimal('95.0'),
            hypertension_history='yes', smoking_history='no', sedentary_minutes_day=400,
            screening_probability=0.22, ai_referral_recommended=True, decision_threshold=Decimal('0.1389')
        )
        ScreeningExplanation.objects.create(
            screening_record=self.rec1, method="gam_native_additive", intercept=-2.0,
            contributions_json=[], reconstructed_linear_predictor=-1.2, reconstructed_probability=0.22,
            reconstruction_error=0.0001, status='generated'
        )

        # Case 2: Pending Stage 2 (Accepted Refer, no Stage 2)
        self.rec2 = ScreeningRecord.objects.create(
            age=60, sex='female', bmi=Decimal('31.0'), waist_cm=Decimal('98.0'),
            hypertension_history='yes', smoking_history='yes', sedentary_minutes_day=500,
            screening_probability=0.35, ai_referral_recommended=True, decision_threshold=Decimal('0.1389')
        )
        ScreeningExplanation.objects.create(
            screening_record=self.rec2, method="gam_native_additive", intercept=-2.0,
            contributions_json=[], reconstructed_linear_predictor=-0.6, reconstructed_probability=0.35,
            reconstruction_error=0.0001, status='generated'
        )
        self.rev2 = HumanReview.objects.create(
            screening_record=self.rec2, reviewer_code="R102", review_action="accepted",
            final_referral_recommended=True
        )

        # Case 3: Completed Two-Stage (Should be EXCLUDED from queue)
        self.rec3 = ScreeningRecord.objects.create(
            age=65, sex='male', bmi=Decimal('30.0'), waist_cm=Decimal('100.0'),
            hypertension_history='yes', smoking_history='yes', sedentary_minutes_day=600,
            screening_probability=0.42, ai_referral_recommended=True, decision_threshold=Decimal('0.1389')
        )
        ScreeningExplanation.objects.create(
            screening_record=self.rec3, method="gam_native_additive", intercept=-2.0,
            contributions_json=[], reconstructed_linear_predictor=-0.3, reconstructed_probability=0.42,
            reconstruction_error=0.0001, status='generated'
        )
        rev3 = HumanReview.objects.create(
            screening_record=self.rec3, reviewer_code="R103", review_action="accepted",
            final_referral_recommended=True
        )
        Stage2Assessment.objects.create(
            human_review=rev3, hba1c_percent=Decimal('6.80'), laboratory_range='diabetes_range',
            range_rule_version='ADA_2026_A1C_RANGE_V1', entry_method='manual'
        )

        # Case 4: Reviewed No Refer (Should be EXCLUDED from queue)
        self.rec4 = ScreeningRecord.objects.create(
            age=40, sex='female', bmi=Decimal('23.0'), waist_cm=Decimal('78.0'),
            hypertension_history='no', smoking_history='no', sedentary_minutes_day=200,
            screening_probability=0.05, ai_referral_recommended=False, decision_threshold=Decimal('0.1389')
        )
        ScreeningExplanation.objects.create(
            screening_record=self.rec4, method="gam_native_additive", intercept=-2.0,
            contributions_json=[], reconstructed_linear_predictor=-2.9, reconstructed_probability=0.05,
            reconstruction_error=0.0001, status='generated'
        )
        HumanReview.objects.create(
            screening_record=self.rec4, reviewer_code="R104", review_action="accepted",
            final_referral_recommended=False
        )

    def test_queue_inclusions_and_exclusions(self):
        """Review Queue includes only actionable cases (pending review & pending stage 2)."""
        # Check review tab
        res_review = self.client.get(self.url + "?tab=review")
        self.assertEqual(res_review.status_code, 200)
        self.assertEqual(res_review.context['pending_review_count'], 1)
        self.assertEqual(res_review.context['pending_stage2_count'], 1)
        self.assertEqual(res_review.context['total_actionable'], 2)

        # Case 1 is in pending review
        p_review_ids = [str(x['record'].id) for x in res_review.context['pending_review_cases']]
        self.assertIn(str(self.rec1.id), p_review_ids)

        # Case 2 is in pending stage 2
        p_stage2_ids = [str(x['record'].id) for x in res_review.context['pending_stage2_cases']]
        self.assertIn(str(self.rec2.id), p_stage2_ids)

        # Cases 3 (completed) and 4 (no refer) are excluded from both!
        self.assertNotIn(str(self.rec3.id), p_review_ids)
        self.assertNotIn(str(self.rec3.id), p_stage2_ids)
        self.assertNotIn(str(self.rec4.id), p_review_ids)
        self.assertNotIn(str(self.rec4.id), p_stage2_ids)

    def test_queue_zero_database_writes(self):
        """GET request on review queue performs 0 database writes."""
        rec_count = ScreeningRecord.objects.count()
        exp_count = ScreeningExplanation.objects.count()
        rev_count = HumanReview.objects.count()
        s2_count = Stage2Assessment.objects.count()

        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 200)

        self.assertEqual(ScreeningRecord.objects.count(), rec_count)
        self.assertEqual(ScreeningExplanation.objects.count(), exp_count)
        self.assertEqual(HumanReview.objects.count(), rev_count)
        self.assertEqual(Stage2Assessment.objects.count(), s2_count)

    def test_queue_zero_ml_and_xai(self):
        """GET request on review queue executes 0 GAM inference and 0 XAI calculations."""
        with mock.patch('predictor.services.screening_inference.predict_screening') as mock_inf:
            with mock.patch('predictor.services.screening_explanation.explain_screening') as mock_exp:
                res = self.client.get(self.url)
                self.assertEqual(res.status_code, 200)
                mock_inf.assert_not_called()
                mock_exp.assert_not_called()


class ScreeningHistoryIntegrationTests(TestCase):
    """Integration tests verifying Screening History ledger, pagination, filtering, and search."""

    def setUp(self):
        self.client = Client()
        self.url = reverse('predictor:history')

        # Create 3 distinct cases
        # Case A: Completed Stage 2 (Refer, Accepted, Diabetes-range)
        self.rec_a = ScreeningRecord.objects.create(
            age=62, sex='male', bmi=Decimal('31.2'), waist_cm=Decimal('102.0'),
            hypertension_history='yes', smoking_history='yes', sedentary_minutes_day=500,
            screening_probability=0.38, ai_referral_recommended=True, decision_threshold=Decimal('0.1389')
        )
        ScreeningExplanation.objects.create(
            screening_record=self.rec_a, method="gam_native_additive", intercept=-2.0,
            contributions_json=[], reconstructed_linear_predictor=-0.5, reconstructed_probability=0.38,
            reconstruction_error=0.0001, status='generated'
        )
        rev_a = HumanReview.objects.create(
            screening_record=self.rec_a, reviewer_code="R201", review_action="accepted",
            final_referral_recommended=True
        )
        Stage2Assessment.objects.create(
            human_review=rev_a, hba1c_percent=Decimal('7.10'), laboratory_range='diabetes_range',
            range_rule_version='ADA_2026_A1C_RANGE_V1', entry_method='manual'
        )

        # Case B: Overridden to Do Not Refer (Refer, Overridden, No Refer, Stage 2 Not applicable)
        self.rec_b = ScreeningRecord.objects.create(
            age=51, sex='female', bmi=Decimal('27.5'), waist_cm=Decimal('90.0'),
            hypertension_history='yes', smoking_history='no', sedentary_minutes_day=300,
            screening_probability=0.18, ai_referral_recommended=True, decision_threshold=Decimal('0.1389')
        )
        ScreeningExplanation.objects.create(
            screening_record=self.rec_b, method="gam_native_additive", intercept=-2.0,
            contributions_json=[], reconstructed_linear_predictor=-1.5, reconstructed_probability=0.18,
            reconstruction_error=0.0001, status='generated'
        )
        HumanReview.objects.create(
            screening_record=self.rec_b, reviewer_code="R202", review_action="overridden",
            final_referral_recommended=False, override_reason_code="additional_context_reduces_concern"
        )

        # Case C: Overridden to Refer (No Refer, Overridden, Refer, Stage 2 Pending)
        self.rec_c = ScreeningRecord.objects.create(
            age=48, sex='male', bmi=Decimal('24.0'), waist_cm=Decimal('82.0'),
            hypertension_history='no', smoking_history='no', sedentary_minutes_day=200,
            screening_probability=0.08, ai_referral_recommended=False, decision_threshold=Decimal('0.1389')
        )
        ScreeningExplanation.objects.create(
            screening_record=self.rec_c, method="gam_native_additive", intercept=-2.0,
            contributions_json=[], reconstructed_linear_predictor=-2.4, reconstructed_probability=0.08,
            reconstruction_error=0.0001, status='generated'
        )
        HumanReview.objects.create(
            screening_record=self.rec_c, reviewer_code="R203", review_action="overridden",
            final_referral_recommended=True, override_reason_code="additional_context_increases_concern"
        )

    def test_one_row_per_screening_record(self):
        """History ledger produces exactly 1 item per ScreeningRecord."""
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.context['records']), 3)

    def test_ai_vs_human_decision_separation(self):
        """History separates AI Recommendation from Final Human Decision."""
        res = self.client.get(self.url)
        content = res.content.decode('utf-8')

        # Th elements must verify separate columns
        self.assertIn('<th scope="col">AI Recommendation</th>', content)
        self.assertIn('<th scope="col">Final Human Decision</th>', content)
        self.assertIn('<th scope="col">Review Action</th>', content)

    def test_stage2_not_applicable_vs_pending_distinction(self):
        """Case B has Stage 2 'Not applicable' while Case C has Stage 2 'Pending'."""
        res = self.client.get(self.url)
        record_map = {str(item['record'].id): item for item in res.context['records']}

        # Case B: final decision is False -> Not applicable
        self.assertEqual(record_map[str(self.rec_b.id)]['lifecycle'].stage2_status_code, 'not_applicable')
        self.assertEqual(record_map[str(self.rec_b.id)]['lifecycle'].stage2_status_label, 'Not applicable')

        # Case C: final decision is True and no Stage 2 -> Pending
        self.assertEqual(record_map[str(self.rec_c.id)]['lifecycle'].stage2_status_code, 'pending')
        self.assertEqual(record_map[str(self.rec_c.id)]['lifecycle'].stage2_status_label, 'Pending')

        # Case A: completed -> Completed
        self.assertEqual(record_map[str(self.rec_a.id)]['lifecycle'].stage2_status_code, 'completed')
        self.assertEqual(record_map[str(self.rec_a.id)]['lifecycle'].stage2_status_label, 'Completed')

    def test_history_search_by_uuid(self):
        """Search by valid Screening UUID filters down to exactly that record."""
        target_uuid = str(self.rec_a.id)
        res = self.client.get(self.url, {'search': target_uuid})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.context['records']), 1)
        self.assertEqual(str(res.context['records'][0]['record'].id), target_uuid)

    def test_history_search_by_partial_uuid(self):
        """Search by first 8 characters of UUID finds the matching record."""
        partial_uuid = str(self.rec_b.id)[:8]
        res = self.client.get(self.url, {'search': partial_uuid})
        self.assertEqual(res.status_code, 200)
        matched_ids = [str(r['record'].id) for r in res.context['records']]
        self.assertIn(str(self.rec_b.id), matched_ids)

    def test_history_search_nonexistent_uuid_returns_empty(self):
        """Search for nonexistent UUID returns safe empty state."""
        res = self.client.get(self.url, {'search': '00000000-0000-0000-0000-000000000000'})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.context['records']), 0)
        content = res.content.decode('utf-8')
        self.assertIn("no matching records", content.lower())

    def test_history_filtering_combinations(self):
        """Test multi-parameter filter combinations."""
        # 1. Overridden cases (Cases B and C)
        res_overridden = self.client.get(self.url, {'review_action': 'overridden'})
        self.assertEqual(len(res_overridden.context['records']), 2)

        # 2. Overridden + Final Refer (Case C only)
        res_overridden_refer = self.client.get(self.url, {
            'review_action': 'overridden',
            'final_decision': 'refer',
        })
        self.assertEqual(len(res_overridden_refer.context['records']), 1)
        self.assertEqual(str(res_overridden_refer.context['records'][0]['record'].id), str(self.rec_c.id))

        # 3. Completed Stage 2 (Case A only)
        res_completed = self.client.get(self.url, {'stage2_status': 'completed'})
        self.assertEqual(len(res_completed.context['records']), 1)
        self.assertEqual(str(res_completed.context['records'][0]['record'].id), str(self.rec_a.id))

    def test_history_zero_ml_and_xai(self):
        """GET request on history executes 0 GAM inference and 0 XAI calculations."""
        with mock.patch('predictor.services.screening_inference.predict_screening') as mock_inf:
            with mock.patch('predictor.services.screening_explanation.explain_screening') as mock_exp:
                res = self.client.get(self.url)
                self.assertEqual(res.status_code, 200)
                mock_inf.assert_not_called()
                mock_exp.assert_not_called()

    def test_history_immutability_guarantee(self):
        """GET requests across queue, history, and detail views perform 0 record mutations."""
        # Pre-check timestamps and field values
        a_prob = self.rec_a.screening_probability
        a_updated = self.rec_a.created_at

        # Execute GET requests
        self.client.get(reverse('predictor:review_queue'))
        self.client.get(reverse('predictor:history'))
        self.client.get(reverse('predictor:history') + '?status=pending_review')
        self.client.get(reverse('predictor:screening_result', kwargs={'screening_id': self.rec_a.id}))
        self.client.get(reverse('predictor:overview'))

        # Post-check: unchanged
        self.rec_a.refresh_from_db()
        self.assertEqual(self.rec_a.screening_probability, a_prob)
        self.assertEqual(self.rec_a.created_at, a_updated)


class QueryPerformanceAndOptimizationTests(TestCase):
    """Integration tests verifying constant bounded queries and N+1 query prevention using select_related."""

    def setUp(self):
        self.client = Client()
        # Seed 10 records across various lifecycle states
        for i in range(10):
            ai_rec = bool(i % 2 == 0)
            rec = ScreeningRecord.objects.create(
                age=40 + i, sex='female' if i % 2 == 0 else 'male', bmi=Decimal('26.0') + Decimal(str(i * 0.5)),
                waist_cm=Decimal('85.0') + Decimal(str(i)),
                hypertension_history='yes' if i % 3 == 0 else 'no',
                smoking_history='no',
                sedentary_minutes_day=300 + i * 20,
                screening_probability=0.20 if ai_rec else 0.08,
                ai_referral_recommended=ai_rec,
                decision_threshold=Decimal('0.1389'),
            )
            ScreeningExplanation.objects.create(
                screening_record=rec, method="gam_native_additive", intercept=-2.0,
                contributions_json=[], reconstructed_linear_predictor=-1.5,
                reconstructed_probability=rec.screening_probability,
                reconstruction_error=0.0001, status='generated'
            )
            if i >= 3:
                rev = HumanReview.objects.create(
                    screening_record=rec, reviewer_code=f"R{i:03d}", review_action="accepted",
                    final_referral_recommended=ai_rec
                )
                if i >= 7 and ai_rec:
                    Stage2Assessment.objects.create(
                        human_review=rev, hba1c_percent=Decimal('6.20'), laboratory_range='prediabetes_range',
                        range_rule_version='ADA_2026_A1C_RANGE_V1', entry_method='manual'
                    )

    def test_review_queue_bounded_queries(self):
        """Review Queue uses select_related to load all relational entities in a bounded single query."""
        with self.assertNumQueries(1):
            res = self.client.get(reverse('predictor:review_queue'))
            self.assertEqual(res.status_code, 200)

    def test_history_bounded_queries(self):
        """History ledger query executes bounded queries without N+1 per-record lookups."""
        # 1 query for total count + 1 query for select_related dataset
        with self.assertNumQueries(2):
            res = self.client.get(reverse('predictor:history'))
            self.assertEqual(res.status_code, 200)
            self.assertEqual(len(res.context['records']), 10)


# ==============================================================================
# PHASE D2.10: RESEARCH ANALYTICS & HUMAN-AI DECISION FLOW TESTS
# ==============================================================================

from .services.research_analytics import (
    compute_research_analytics,
    safe_rate,
    ResearchAnalyticsSnapshot,
    DecisionTransitionMatrix,
)
from datetime import timedelta, date
from django.utils import timezone
from unittest import mock


class ResearchAnalyticsServiceUnitTests(TestCase):
    """
    Unit tests for ResearchAnalyticsService verifying mathematical definitions,
    exact denominators, division-by-zero safeguards, and data invariants.
    """

    def setUp(self):
        # Build 8 canonical synthetic fixtures representing all cascade paths:
        # Fixture A: AI Refer + Accepted + Stage2 Normal-range
        self.rec_a = self._create_screening(ai_refer=True, prob=0.25)
        self.exp_a = self._create_explanation(self.rec_a, status='generated')
        self.rev_a = self._create_review(self.rec_a, action='accepted', final_refer=True)
        self.s2_a = self._create_stage2(self.rev_a, hba1c=Decimal('5.40'), range_cat='normal_range')

        # Fixture B: AI Refer + Accepted + Stage2 Prediabetes-range
        self.rec_b = self._create_screening(ai_refer=True, prob=0.30)
        self.exp_b = self._create_explanation(self.rec_b, status='generated')
        self.rev_b = self._create_review(self.rec_b, action='accepted', final_refer=True)
        self.s2_b = self._create_stage2(self.rev_b, hba1c=Decimal('6.10'), range_cat='prediabetes_range')

        # Fixture C: AI Refer + Override No Refer
        self.rec_c = self._create_screening(ai_refer=True, prob=0.18)
        self.exp_c = self._create_explanation(self.rec_c, status='generated')
        self.rev_c = self._create_review(
            self.rec_c,
            action='overridden',
            final_refer=False,
            reason='additional_context_reduces_concern'
        )

        # Fixture D: AI No Refer + Accepted
        self.rec_d = self._create_screening(ai_refer=False, prob=0.08)
        self.exp_d = self._create_explanation(self.rec_d, status='generated')
        self.rev_d = self._create_review(self.rec_d, action='accepted', final_refer=False)

        # Fixture E: AI No Refer + Override Refer + Stage2 Diabetes-range
        self.rec_e = self._create_screening(ai_refer=False, prob=0.12)
        self.exp_e = self._create_explanation(self.rec_e, status='generated')
        self.rev_e = self._create_review(
            self.rec_e,
            action='overridden',
            final_refer=True,
            reason='additional_context_increases_concern'
        )
        self.s2_e = self._create_stage2(self.rev_e, hba1c=Decimal('7.20'), range_cat='diabetes_range')

        # Fixture F: Pending Human Review (Faithful explanation available)
        self.rec_f = self._create_screening(ai_refer=True, prob=0.22)
        self.exp_f = self._create_explanation(self.rec_f, status='generated')

        # Fixture G: Explanation Unavailable (XAI generation failure)
        self.rec_g = self._create_screening(ai_refer=False, prob=0.05)
        self.exp_g = self._create_explanation(self.rec_g, status='failed')

        # Fixture H: Pending Stage 2 (Authorized final referral without lab intake)
        self.rec_h = self._create_screening(ai_refer=True, prob=0.35)
        self.exp_h = self._create_explanation(self.rec_h, status='generated')
        self.rev_h = self._create_review(self.rec_h, action='accepted', final_refer=True)

    def _create_screening(self, ai_refer=True, prob=0.25):
        return ScreeningRecord.objects.create(
            age=52,
            sex='female',
            bmi=Decimal('28.5'),
            waist_cm=Decimal('92.0'),
            hypertension_history='yes',
            smoking_history='no',
            sedentary_minutes_day=360,
            screening_probability=prob,
            ai_referral_recommended=ai_refer,
            decision_threshold=Decimal('0.1389'),
        )

    def _create_explanation(self, record, status='generated'):
        return ScreeningExplanation.objects.create(
            screening_record=record,
            method="gam_native_additive",
            intercept=-2.365,
            contributions_json=[],
            reconstructed_linear_predictor=-1.077,
            reconstructed_probability=0.254,
            reconstruction_error=0.0001,
            status=status,
        )

    def _create_review(self, record, action='accepted', final_refer=True, reason=None, note=None):
        rev = HumanReview(
            screening_record=record,
            reviewer_code='R-TEST',
            review_action=action,
            final_referral_recommended=final_refer,
            override_reason_code=reason or '',
            override_note=note or '',
        )
        rev.save()
        return rev

    def _create_stage2(self, review, hba1c=Decimal('5.50'), range_cat='normal_range'):
        return Stage2Assessment.objects.create(
            human_review=review,
            hba1c_percent=hba1c,
            laboratory_range=range_cat,
            range_rule_version='ADA_2026_A1C_RANGE_V1',
            entry_method='manual',
        )

    def test_total_screenings_and_ai_referral_rate(self):
        """Total screenings and AI referral rate must match exact counts and N_screenings denominator."""
        snap = compute_research_analytics()
        self.assertEqual(snap.total_screenings, 8)
        self.assertEqual(snap.ai_refer_count, 5)  # A, B, C, F, H
        self.assertEqual(snap.ai_no_refer_count, 3)  # D, E, G
        # 5 / 8 = 62.5%
        self.assertEqual(snap.ai_refer_rate, 62.5)

    def test_review_completion_rate_denominator(self):
        """Review completion rate denominator is strictly N_review_eligible (generated XAI)."""
        snap = compute_research_analytics()
        # 8 screenings, 7 generated, 1 failed (G)
        self.assertEqual(snap.review_eligible_count, 7)
        self.assertEqual(snap.explanation_unavailable_count, 1)
        # 6 reviewed: A, B, C, D, E, H
        self.assertEqual(snap.reviewed_count, 6)
        # 6 / 7 = 85.7%
        self.assertEqual(snap.review_completion_rate, 85.7)

    def test_human_ai_agreement_and_override_denominators(self):
        """Agreement and override rate denominators are strictly reviewed cases (N_reviewed)."""
        snap = compute_research_analytics()
        # 6 reviewed cases: A, B, C, D, E, H
        # Accepted: A, B, D, H = 4
        # Overridden: C, E = 2
        self.assertEqual(snap.accepted_count, 4)
        self.assertEqual(snap.overridden_count, 2)
        # Agreement rate: 4 / 6 = 66.7%
        self.assertEqual(snap.agreement_rate, 66.7)
        # Override rate: 2 / 6 = 33.3%
        self.assertEqual(snap.override_rate, 33.3)

    def test_agreement_plus_override_invariant(self):
        """Accepted + Overridden must equal Reviewed, and sum of rates equals 100% within rounding."""
        snap = compute_research_analytics()
        self.assertEqual(snap.accepted_count + snap.overridden_count, snap.reviewed_count)
        self.assertAlmostEqual(snap.agreement_rate + snap.override_rate, 100.0, places=1)

    def test_final_human_referral_rate_denominator(self):
        """Final human referral rate denominator is reviewed cases (N_reviewed)."""
        snap = compute_research_analytics()
        # Final referrals: A, B, E, H = 4 of 6 reviewed
        self.assertEqual(snap.final_refer_count, 4)
        self.assertEqual(snap.final_no_refer_count, 2)  # C, D
        self.assertEqual(snap.final_referral_rate, 66.7)

    def test_stage2_completion_rate_denominator(self):
        """Stage-2 completion rate denominator is strictly eligible final referrals (N_stage2_eligible)."""
        snap = compute_research_analytics()
        # Final referrals = 4 (A, B, E, H)
        self.assertEqual(snap.stage2_eligible_count, 4)
        # Completed Stage-2 = 3 (A, B, E)
        self.assertEqual(snap.stage2_completed_count, 3)
        # 3 / 4 = 75.0% (NOT 3 / 8 = 37.5% of all screenings)
        self.assertEqual(snap.stage2_completion_rate, 75.0)

    def test_stage2_laboratory_range_distribution(self):
        """Stage-2 laboratory range distribution denominator is strictly N_stage2_completed."""
        snap = compute_research_analytics()
        self.assertEqual(snap.stage2_completed_count, 3)
        self.assertEqual(snap.stage2_normal_count, 1)        # A
        self.assertEqual(snap.stage2_prediabetes_count, 1)   # B
        self.assertEqual(snap.stage2_diabetes_count, 1)      # E
        # 1 / 3 = 33.3%
        self.assertEqual(snap.stage2_normal_rate, 33.3)
        self.assertEqual(snap.stage2_prediabetes_rate, 33.3)
        self.assertEqual(snap.stage2_diabetes_rate, 33.3)
        # Sum of categories must equal N_stage2_completed
        self.assertEqual(
            snap.stage2_normal_count + snap.stage2_prediabetes_count + snap.stage2_diabetes_count,
            snap.stage2_completed_count,
        )

    def test_decision_transition_matrix_invariants(self):
        """2x2 transition matrix cells must sum to N_reviewed, with diagonal=accepted, off-diagonal=overridden."""
        snap = compute_research_analytics()
        m = snap.transition_matrix
        # AI Refer -> Human Refer: A, B, H = 3
        self.assertEqual(m.ai_refer_human_refer, 3)
        # AI Refer -> Human No Refer: C = 1
        self.assertEqual(m.ai_refer_human_no_refer, 1)
        # AI No Refer -> Human Refer: E = 1
        self.assertEqual(m.ai_no_refer_human_refer, 1)
        # AI No Refer -> Human No Refer: D = 1
        self.assertEqual(m.ai_no_refer_human_no_refer, 1)

        # Invariants:
        self.assertEqual(m.total_cells, snap.reviewed_count)
        self.assertEqual(m.diagonal_sum, snap.accepted_count)
        self.assertEqual(m.off_diagonal_sum, snap.overridden_count)

    def test_override_direction_split(self):
        """Override direction counts sum to N_overridden with correct percentages."""
        snap = compute_research_analytics()
        self.assertEqual(snap.overridden_count, 2)
        self.assertEqual(snap.override_away_count, 1)    # C
        self.assertEqual(snap.override_toward_count, 1)  # E
        self.assertEqual(snap.override_away_rate, 50.0)
        self.assertEqual(snap.override_toward_rate, 50.0)

    def test_override_structured_reasons(self):
        """Structured override reasons must be tracked by branch without analyzing free text."""
        snap = compute_research_analytics()
        # Branch Refer -> No Refer
        r_away = {item.code: item for item in snap.reasons_refer_to_no_refer}
        self.assertEqual(r_away['additional_context_reduces_concern'].count, 1)
        self.assertEqual(r_away['additional_context_reduces_concern'].rate, 100.0)

        # Branch No Refer -> Refer
        r_toward = {item.code: item for item in snap.reasons_no_refer_to_refer}
        self.assertEqual(r_toward['additional_context_increases_concern'].count, 1)
        self.assertEqual(r_toward['additional_context_increases_concern'].rate, 100.0)

    def test_division_by_zero_safety(self):
        """When denominators are zero, rates must strictly return None, never 0.0 or raise error."""
        self.assertIsNone(safe_rate(0, 0))
        self.assertIsNone(safe_rate(5, 0))

        # Query on empty queryset
        empty_snap = compute_research_analytics(queryset=ScreeningRecord.objects.none())
        self.assertEqual(empty_snap.total_screenings, 0)
        self.assertIsNone(empty_snap.ai_refer_rate)
        self.assertIsNone(empty_snap.review_completion_rate)
        self.assertIsNone(empty_snap.agreement_rate)
        self.assertIsNone(empty_snap.override_rate)
        self.assertIsNone(empty_snap.final_referral_rate)
        self.assertIsNone(empty_snap.stage2_completion_rate)
        self.assertIsNone(empty_snap.stage2_normal_rate)
        self.assertIsNone(empty_snap.override_away_rate)
        self.assertIsNone(empty_snap.override_toward_rate)

    def test_legacy_records_exclusion(self):
        """Legacy Prediction and Override entities must not be counted in analytics."""
        Prediction.objects.create(
            patient_data={'age': 60, 'bmi': 30.0},
            model_used='xgboost',
            prediction=1,
            confidence=0.85,
        )
        # Recalculate
        snap = compute_research_analytics()
        self.assertEqual(snap.total_screenings, 8)  # Still 8, legacy ignored

    def test_date_filtering(self):
        """Date filtering on created_at restricts primary population cleanly."""
        today = timezone.now().date()
        yesterday = today - timedelta(days=1)
        tomorrow = today + timedelta(days=1)

        # Update rec_a to yesterday
        ScreeningRecord.objects.filter(id=self.rec_a.id).update(
            created_at=timezone.now() - timedelta(days=1)
        )

        # Filter strictly for today
        snap_today = compute_research_analytics(date_from=today, date_to=today)
        self.assertEqual(snap_today.total_screenings, 7)

        # Filter strictly for yesterday
        snap_yesterday = compute_research_analytics(date_from=yesterday, date_to=yesterday)
        self.assertEqual(snap_yesterday.total_screenings, 1)

    def test_query_efficiency_bounded_sql(self):
        """Computing complete analytics snapshot requires exactly 2 bounded SQL queries."""
        with self.assertNumQueries(2):
            compute_research_analytics()


class ResearchAnalyticsViewIntegrationTests(TestCase):
    """
    Integration tests for /analytics/ view verifying read-only semantics,
    zero ML/XAI execution, zero database writes, and visual templates.
    """

    def setUp(self):
        self.client = Client()
        # Create minimal valid screening cascade
        rec = ScreeningRecord.objects.create(
            age=45,
            sex='male',
            bmi=Decimal('27.0'),
            waist_cm=Decimal('88.0'),
            hypertension_history='no',
            smoking_history='yes',
            sedentary_minutes_day=240,
            screening_probability=0.18,
            ai_referral_recommended=True,
            decision_threshold=Decimal('0.1389'),
        )
        exp = ScreeningExplanation.objects.create(
            screening_record=rec,
            method="gam_native_additive",
            intercept=-2.365,
            contributions_json=[],
            reconstructed_linear_predictor=-1.077,
            reconstructed_probability=0.18,
            reconstruction_error=0.0001,
            status='generated',
        )
        rev = HumanReview.objects.create(
            screening_record=rec,
            reviewer_code='R-TEST',
            review_action='accepted',
            final_referral_recommended=True,
        )
        Stage2Assessment.objects.create(
            human_review=rev,
            hba1c_percent=Decimal('5.80'),
            laboratory_range='prediabetes_range',
            range_rule_version='ADA_2026_A1C_RANGE_V1',
        )

    def test_analytics_view_get_200(self):
        """GET /analytics/ returns 200 with complete analytics snapshot in context."""
        response = self.client.get(reverse('predictor:analytics'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('analytics', response.context)
        self.assertTemplateUsed(response, 'predictor/analytics.html')
        self.assertContains(response, 'Research Analytics')
        self.assertContains(response, 'Human–AI Decision Transition Matrix')
        self.assertContains(response, 'Observed HbA1c Laboratory-Range Distribution')

    def test_analytics_view_date_filtering(self):
        """GET /analytics/?date_from=...&date_to=... filters analytics correctly."""
        today_str = timezone.now().strftime('%Y-%m-%d')
        response = self.client.get(reverse('predictor:analytics'), {
            'date_from': today_str,
            'date_to': today_str,
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['has_active_filter'])
        self.assertEqual(response.context['analytics'].total_screenings, 1)

    def test_analytics_view_empty_state_and_na_display(self):
        """On empty database, /analytics/ renders clean empty states and 'Not available' / '—' without error."""
        # Purge all records
        Stage2Assessment.objects.all().delete()
        HumanReview.objects.all().delete()
        ScreeningExplanation.objects.all().delete()
        ScreeningRecord.objects.all().delete()

        response = self.client.get(reverse('predictor:analytics'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['analytics'].total_screenings, 0)
        self.assertContains(response, 'Not available')
        self.assertContains(response, 'Human–AI agreement is not yet available because no screenings have been reviewed.')

    def test_zero_database_writes_on_get(self):
        """GET /analytics/ performs zero database writes (read-only invariant)."""
        counts_before = {
            'screening': ScreeningRecord.objects.count(),
            'explanation': ScreeningExplanation.objects.count(),
            'review': HumanReview.objects.count(),
            'stage2': Stage2Assessment.objects.count(),
        }
        res = self.client.get(reverse('predictor:analytics'))
        self.assertEqual(res.status_code, 200)
        counts_after = {
            'screening': ScreeningRecord.objects.count(),
            'explanation': ScreeningExplanation.objects.count(),
            'review': HumanReview.objects.count(),
            'stage2': Stage2Assessment.objects.count(),
        }
        self.assertEqual(counts_before, counts_after)

    def test_zero_ml_and_xai_execution(self):
        """GET /analytics/ executes zero GAM model inference and zero XAI calculations."""
        with mock.patch('predictor.services.screening_inference.predict_screening') as mock_inf, \
             mock.patch('predictor.services.screening_explanation.explain_screening') as mock_xai, \
             mock.patch('predictor.services.hba1c_range.classify_hba1c_range') as mock_hba1c:
            res = self.client.get(reverse('predictor:analytics'))
            self.assertEqual(res.status_code, 200)
            mock_inf.assert_not_called()
            mock_xai.assert_not_called()
            mock_hba1c.assert_not_called()


class ProhibitedPerformanceMetricsSafetyTests(TestCase):
    """
    Source code and algorithmic audit ensuring operational Stage-2 records
    are NEVER used to compute predictive performance metrics (verification bias safeguard).
    """

    def test_no_scikit_learn_performance_metrics_in_analytics(self):
        """Ensure research_analytics service does not import or execute diagnostic accuracy functions."""
        from .services import research_analytics
        import inspect
        import ast

        source = inspect.getsource(research_analytics)
        tree = ast.parse(source)

        # 1. Assert sklearn.metrics is NEVER imported
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    self.assertNotIn('sklearn.metrics', alias.name)
            elif isinstance(node, ast.ImportFrom):
                self.assertNotEqual(node.module, 'sklearn.metrics')
                if node.module:
                    self.assertNotIn('sklearn.metrics', node.module)

        # 2. Assert prohibited performance identifiers are never called or defined
        prohibited = [
            'accuracy_score',
            'roc_auc_score',
            'average_precision_score',
            'confusion_matrix',
            'precision_score',
            'recall_score',
            'f1_score',
            'override_success_rate',
        ]
        for term in prohibited:
            self.assertNotIn(
                term,
                source,
                f"Prohibited performance term '{term}' detected in research_analytics service!"
            )


# ==============================================================================
# PHASE D3: FINAL SYSTEM AUDIT & USER-STUDY READINESS TEST SUITE
# ==============================================================================

class PhaseD3SystemAuditTests(TestCase):
    """
    Exhaustive verification of D3 requirements:
    1. Complete End-to-End Scenarios Matrix (Scenarios A through H)
    2. Data Isolation & Zero-State behavior
    3. Failure modes & No Silent Fallbacks
    4. Protected Artifact Hashes & Single Decision Authority
    """

    def setUp(self):
        self.client = Client()
        self.valid_input_refer = {
            'age': 55,
            'sex': 'male',
            'bmi': '31.2',
            'waist_cm': '104.0',
            'hypertension_history': 'yes',
            'smoking_history': 'yes',
            'sedentary_minutes_day': 480,
        }
        self.valid_input_no_refer = {
            'age': 24,
            'sex': 'female',
            'bmi': '21.0',
            'waist_cm': '72.0',
            'hypertension_history': 'no',
            'smoking_history': 'no',
            'sedentary_minutes_day': 180,
        }

    def test_scenario_a_refer_accept_stage2_normal(self):
        """Scenario A: AI Refer -> Accept -> final Refer -> Stage2 -> Normal -> Completed."""
        # 1. Submit Screening
        res = self.client.post(reverse('predictor:run_screening'), self.valid_input_refer, follow=True)
        self.assertEqual(res.status_code, 200)
        record = ScreeningRecord.objects.latest('created_at')
        self.assertTrue(record.ai_referral_recommended)
        self.assertTrue(hasattr(record, 'explanation'))

        # 2. Review Accept
        accept_res = self.client.post(reverse('predictor:accept_review', kwargs={'screening_id': record.id}), {
            'reviewer_code': 'REV-D3-01',
            'review_notes': 'Accepted by protocol.'
        }, follow=True)
        self.assertEqual(accept_res.status_code, 200)
        review = HumanReview.objects.get(screening_record=record)
        self.assertEqual(review.review_action, 'accepted')
        self.assertTrue(review.final_referral_recommended)

        # 3. Stage 2 Normal (e.g. 5.4%)
        s2_res = self.client.post(reverse('predictor:stage2_confirm', kwargs={'screening_id': record.id}), {
            'hba1c_percent': '5.4',
        }, follow=True)
        self.assertEqual(s2_res.status_code, 200)
        s2 = Stage2Assessment.objects.get(human_review=review)
        self.assertEqual(s2.laboratory_range, 'normal_range')

        # 4. Lifecycle state is Completed
        state = derive_screening_lifecycle(record)
        self.assertEqual(state.code, STATE_COMPLETED_STAGE2)

    def test_scenario_b_refer_accept_stage2_prediabetes(self):
        """Scenario B: AI Refer -> Accept -> final Refer -> Stage2 -> Prediabetes -> Completed."""
        res = self.client.post(reverse('predictor:run_screening'), self.valid_input_refer, follow=True)
        record = ScreeningRecord.objects.latest('created_at')
        self.client.post(reverse('predictor:accept_review', kwargs={'screening_id': record.id}), {
            'reviewer_code': 'REV-D3-02',
        }, follow=True)
        review = HumanReview.objects.get(screening_record=record)

        s2_res = self.client.post(reverse('predictor:stage2_confirm', kwargs={'screening_id': record.id}), {
            'hba1c_percent': '6.1',
        }, follow=True)
        self.assertEqual(s2_res.status_code, 200)
        s2 = Stage2Assessment.objects.get(human_review=review)
        self.assertEqual(s2.laboratory_range, 'prediabetes_range')
        self.assertEqual(derive_screening_lifecycle(record).code, STATE_COMPLETED_STAGE2)

    def test_scenario_c_refer_override_no_refer_stage2_blocked(self):
        """Scenario C: AI Refer -> Override to No Refer -> Stage2 unavailable -> Reviewed No Stage2."""
        res = self.client.post(reverse('predictor:run_screening'), self.valid_input_refer, follow=True)
        record = ScreeningRecord.objects.latest('created_at')

        override_res = self.client.post(reverse('predictor:override_review', kwargs={'screening_id': record.id}), {
            'reviewer_code': 'REV-D3-03',
            'override_reason_code': 'additional_context_reduces_concern',
            'override_note': 'Documented normal glycemic tests recently.'
        }, follow=True)
        self.assertEqual(override_res.status_code, 200)
        review = HumanReview.objects.get(screening_record=record)
        self.assertEqual(review.review_action, 'overridden')
        self.assertFalse(review.final_referral_recommended)

        # Stage 2 must redirect with unavailable notification
        s2_page = self.client.get(reverse('predictor:stage2', kwargs={'screening_id': record.id}), follow=True)
        self.assertEqual(s2_page.status_code, 200)
        self.assertContains(s2_page, 'Stage-2 assessment is unavailable because the final human review decision does not recommend referral.')

        # Stage 2 confirm must reject (redirects with error)
        s2_confirm = self.client.post(reverse('predictor:stage2_confirm', kwargs={'screening_id': record.id}), {
            'hba1c_percent': '5.8'
        })
        self.assertEqual(s2_confirm.status_code, 302)
        self.assertEqual(derive_screening_lifecycle(record).code, STATE_REVIEWED_NO_REFERRAL)

    def test_scenario_d_no_refer_accept_stage2_blocked(self):
        """Scenario D: AI No Refer -> Accept -> final No Refer -> Stage2 unavailable."""
        res = self.client.post(reverse('predictor:run_screening'), self.valid_input_no_refer, follow=True)
        record = ScreeningRecord.objects.latest('created_at')
        self.assertFalse(record.ai_referral_recommended)

        self.client.post(reverse('predictor:accept_review', kwargs={'screening_id': record.id}), {
            'reviewer_code': 'REV-D3-04',
        }, follow=True)
        review = HumanReview.objects.get(screening_record=record)
        self.assertFalse(review.final_referral_recommended)

        s2_page = self.client.get(reverse('predictor:stage2', kwargs={'screening_id': record.id}), follow=True)
        self.assertEqual(s2_page.status_code, 200)
        self.assertContains(s2_page, 'Stage-2 assessment is unavailable because the final human review decision does not recommend referral.')
        self.assertEqual(derive_screening_lifecycle(record).code, STATE_REVIEWED_NO_REFERRAL)

    def test_scenario_e_no_refer_override_refer_stage2_diabetes(self):
        """Scenario E: AI No Refer -> Override to Refer -> Stage2 -> Diabetes-range."""
        res = self.client.post(reverse('predictor:run_screening'), self.valid_input_no_refer, follow=True)
        record = ScreeningRecord.objects.latest('created_at')
        self.assertFalse(record.ai_referral_recommended)

        override_res = self.client.post(reverse('predictor:override_review', kwargs={'screening_id': record.id}), {
            'reviewer_code': 'REV-D3-05',
            'override_reason_code': 'additional_context_increases_concern',
            'override_note': 'High-risk clinical presentation noted during visit.'
        }, follow=True)
        self.assertEqual(override_res.status_code, 200)
        review = HumanReview.objects.get(screening_record=record)
        self.assertEqual(review.review_action, 'overridden')
        self.assertTrue(review.final_referral_recommended)

        # Stage 2 must be accessible
        s2_confirm = self.client.post(reverse('predictor:stage2_confirm', kwargs={'screening_id': record.id}), {
            'hba1c_percent': '7.2',
        }, follow=True)
        self.assertEqual(s2_confirm.status_code, 200)
        s2 = Stage2Assessment.objects.get(human_review=review)
        self.assertEqual(s2.laboratory_range, 'diabetes_range')
        self.assertEqual(derive_screening_lifecycle(record).code, STATE_COMPLETED_STAGE2)

    def test_scenario_f_explanation_failure_preserves_screening_blocks_review(self):
        """Scenario F: Explanation failure preserves screening record but blocks review."""
        with mock.patch('predictor.views.screening_explanation.explain_screening',
                        side_effect=screening_explanation.ScreeningExplanationFidelityError("Simulated XAI error")):
            res = self.client.post(reverse('predictor:run_screening'), self.valid_input_refer, follow=True)
            self.assertEqual(res.status_code, 200)

        record = ScreeningRecord.objects.latest('created_at')
        self.assertEqual(record.explanation.status, 'failed')
        self.assertEqual(derive_screening_lifecycle(record).code, STATE_EXPLANATION_UNAVAILABLE)

        # Attempt to accept review must be redirected/blocked without saving review
        accept_res = self.client.post(reverse('predictor:accept_review', kwargs={'screening_id': record.id}), {
            'reviewer_code': 'REV-FAIL-01'
        })
        self.assertEqual(accept_res.status_code, 302)
        self.assertEqual(HumanReview.objects.filter(screening_record=record).count(), 0)

    def test_scenario_g_inference_failure_halts_persistence(self):
        """Scenario G: Inference failure persists zero records."""
        count_before = ScreeningRecord.objects.count()
        with mock.patch('predictor.views.screening_inference.predict_screening',
                        side_effect=screening_inference.ScreeningInferenceError("Simulated model error")):
            res = self.client.post(reverse('predictor:run_screening'), self.valid_input_refer, follow=True)
            self.assertEqual(res.status_code, 200)
            self.assertContains(res, 'Screening Inference Execution Error')

        count_after = ScreeningRecord.objects.count()
        self.assertEqual(count_before, count_after)

    def test_scenario_h_stage2_invalid_input_halts_persistence(self):
        """Scenario H: Invalid Stage2 input halts Stage2 persistence."""
        res = self.client.post(reverse('predictor:run_screening'), self.valid_input_refer, follow=True)
        record = ScreeningRecord.objects.latest('created_at')
        self.client.post(reverse('predictor:accept_review', kwargs={'screening_id': record.id}), {
            'reviewer_code': 'REV-D3-06',
        }, follow=True)

        s2_count_before = Stage2Assessment.objects.count()
        # Invalid HbA1c value (out of clinical bounds: 1.0% < 2.0%)
        s2_res = self.client.post(reverse('predictor:stage2_confirm', kwargs={'screening_id': record.id}), {
            'hba1c_percent': '1.0',
        })
        self.assertEqual(s2_res.status_code, 302)
        self.assertEqual(Stage2Assessment.objects.count(), s2_count_before)

    def test_data_mode_dev_vs_study_analytics_banner(self):
        """Verify Analytics page displays development banner in dev mode and suppresses in study mode."""
        with self.settings(APP_DATA_MODE='development'):
            res_dev = self.client.get(reverse('predictor:analytics'))
            self.assertEqual(res_dev.status_code, 200)
            self.assertContains(res_dev, 'Development environment — displayed records may include synthetic or QA data.')

        with self.settings(APP_DATA_MODE='study'):
            res_study = self.client.get(reverse('predictor:analytics'))
            self.assertEqual(res_study.status_code, 200)
            self.assertNotContains(res_study, 'Development environment — displayed records may include synthetic or QA data.')

    def test_components_demo_nav_hidden_in_study_mode(self):
        """Verify Design System UI link is omitted from base navigation in study mode."""
        with self.settings(APP_DATA_MODE='study'):
            res = self.client.get(reverse('predictor:overview'))
            self.assertEqual(res.status_code, 200)
            self.assertNotContains(res, 'Design System UI')

    def test_protected_artifact_hashes_integrity(self):
        """Verify that locked artifact SHA256 hashes strictly match the specification."""
        from pathlib import Path
        from .services.screening_inference import (
            compute_file_sha256,
            get_artifact_paths,
            EXPECTED_GAM_SHA256,
            EXPECTED_PREPROCESSOR_SHA256,
        )
        paths = get_artifact_paths()
        self.assertEqual(compute_file_sha256(paths['gam']), EXPECTED_GAM_SHA256)
        self.assertEqual(compute_file_sha256(paths['preprocessor']), EXPECTED_PREPROCESSOR_SHA256)

        # Model specification doc hash
        spec_path = Path(__file__).resolve().parent.parent.parent / 'nhanes_feasibility_2021_2023' / 'lock_phase4_2' / 'FINAL_MODEL_SPECIFICATION_LOCKED.md'
        expected_spec_hash = "7d2a5eb9c349dabfca4f5387161c78833c8e996dc302e16955a4d588d68d9ec5"
        self.assertEqual(compute_file_sha256(spec_path), expected_spec_hash)

        # Final test predictions hash (canonical LF SHA-256)
        pred_path = Path(__file__).resolve().parent.parent.parent / 'nhanes_feasibility_2021_2023' / 'predictions_phase5' / 'final_test_predictions.csv'
        expected_pred_hash = "21c238f25d488e8dad0cfdd12193d099476b46305133d1fd291ca85fd61e7520"
        self.assertEqual(compute_file_sha256(pred_path), expected_pred_hash)

    def test_decision_threshold_single_authority(self):
        """Confirm that FROZEN_DECISION_THRESHOLD is 0.1389 and single authority."""
        from .services.screening_inference import FROZEN_DECISION_THRESHOLD
        self.assertEqual(FROZEN_DECISION_THRESHOLD, 0.1389)

