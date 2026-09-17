"""
Test Suite: Authoritative Backend BMI Calculator & Input Contract
Phase D2.2 / D2.3 Verification

Requirements verified:
1. height_cm + weight_kg input contract
2. Independent backend calculation: 177 cm + 58 kg -> 18.51
3. Independent backend calculation: 170 cm + 70 kg -> 24.22
4. Protection against client BMI tampering (frontend BMI value cannot override backend calculation)
5. Out-of-range calculated BMI triggers validation error
6. Height and weight are NOT added to model predictors (CANONICAL_PREDICTOR_ORDER remains untouched)
7. End-to-end run_screening persists authoritative calculated BMI
8. Backward compatibility for legacy tests supplying raw BMI
"""

from decimal import Decimal
import uuid
from django.test import TestCase, Client
from django.urls import reverse
from predictor.forms import Stage1ScreeningForm
from predictor.models import ScreeningRecord
from predictor.services import screening_inference
from predictor.screening_schema import STAGE1_INPUT_SCHEMA


class BMICalculatorBackendTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.base_valid_payload = {
            'age': 45,
            'sex': 'female',
            'waist_cm': 85.0,
            'hypertension_history': 'no',
            'smoking_history': 'no',
            'sedentary_minutes_day': 360,
        }

    def test_calculation_177cm_58kg_yields_18_51(self):
        """177 cm + 58 kg -> 18.51 kg/m²"""
        data = self.base_valid_payload.copy()
        data.update({
            'height_cm': 177.0,
            'weight_kg': 58.0,
        })
        form = Stage1ScreeningForm(data=data)
        self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")
        self.assertEqual(form.cleaned_data['bmi'], Decimal('18.51'))

    def test_calculation_170cm_70kg_yields_24_22(self):
        """170 cm + 70 kg -> 24.22 kg/m²"""
        data = self.base_valid_payload.copy()
        data.update({
            'height_cm': 170.0,
            'weight_kg': 70.0,
        })
        form = Stage1ScreeningForm(data=data)
        self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")
        self.assertEqual(form.cleaned_data['bmi'], Decimal('24.22'))

    def test_frontend_bmi_manipulation_cannot_override_backend_calculation(self):
        """
        Tampering with frontend-submitted BMI value MUST NOT override backend calculation.
        Backend calculation is strictly authoritative.
        """
        data = self.base_valid_payload.copy()
        data.update({
            'height_cm': 170.0,
            'weight_kg': 70.0,
            'bmi': 99.9,  # Maliciously injected / forged client BMI
        })
        form = Stage1ScreeningForm(data=data)
        self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")
        # Value must be 24.22, NOT 99.9
        self.assertEqual(form.cleaned_data['bmi'], Decimal('24.22'))

        # Test another tamper attempt with an artificially low value
        data['bmi'] = 12.0
        form2 = Stage1ScreeningForm(data=data)
        self.assertTrue(form2.is_valid(), f"Form errors: {form2.errors}")
        self.assertEqual(form2.cleaned_data['bmi'], Decimal('24.22'))

    def test_calculated_bmi_out_of_research_range_rejected(self):
        """Calculated BMI outside [11.1, 69.9] must fail validation."""
        # Under minimum: 190 cm + 35 kg -> BMI ~ 9.70 (< 11.1)
        under_data = self.base_valid_payload.copy()
        under_data.update({'height_cm': 190.0, 'weight_kg': 35.0})
        form_under = Stage1ScreeningForm(data=under_data)
        self.assertFalse(form_under.is_valid())
        self.assertIn('weight_kg', form_under.errors)

        # Over maximum: 140 cm + 150 kg -> BMI ~ 76.53 (> 69.9)
        over_data = self.base_valid_payload.copy()
        over_data.update({'height_cm': 140.0, 'weight_kg': 150.0})
        form_over = Stage1ScreeningForm(data=over_data)
        self.assertFalse(form_over.is_valid())
        self.assertIn('weight_kg', form_over.errors)

    def test_height_and_weight_not_model_predictors(self):
        """
        Height and weight must NOT become model predictors.
        CANONICAL_PREDICTOR_ORDER must strictly retain only the 7 frozen predictors.
        """
        self.assertNotIn('height_cm', screening_inference.CANONICAL_PREDICTOR_ORDER)
        self.assertNotIn('weight_kg', screening_inference.CANONICAL_PREDICTOR_ORDER)
        self.assertEqual(len(screening_inference.CANONICAL_PREDICTOR_ORDER), 7)
        self.assertIn('bmi', screening_inference.CANONICAL_PREDICTOR_ORDER)

    def test_legacy_payload_with_bmi_only_preserves_compatibility(self):
        """Automated test suites sending raw 'bmi' directly must still pass."""
        data = self.base_valid_payload.copy()
        data.update({'bmi': 25.5})
        form = Stage1ScreeningForm(data=data)
        self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")
        self.assertEqual(form.cleaned_data['bmi'], Decimal('25.50'))

    def test_end_to_end_run_screening_authoritative_persistence(self):
        """
        POST to run_screening with height_cm and weight_kg must:
        1. Authoritatively calculate BMI (24.22)
        2. Disregard any submitted 'bmi' parameter
        3. Save ScreeningRecord with bmi = Decimal('24.22')
        """
        post_data = self.base_valid_payload.copy()
        post_data.update({
            'idempotency_token': uuid.uuid4().hex,
            'height_cm': 170.0,
            'weight_kg': 70.0,
            'bmi': 50.0,  # Tampered client BMI
        })

        run_url = reverse('predictor:run_screening')
        response = self.client.post(run_url, post_data)
        self.assertEqual(response.status_code, 302)

        record = ScreeningRecord.objects.get(idempotency_token=post_data['idempotency_token'])
        self.assertEqual(record.bmi, Decimal('24.22'))
        self.assertNotEqual(record.bmi, Decimal('50.0'))
