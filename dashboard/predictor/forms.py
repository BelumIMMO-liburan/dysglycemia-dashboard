"""
Django Forms for Stage-1 Non-Laboratory Screening Intake
Phase D2.2 Implementation

Enforces strict server-side validation against the development-domain
bounds defined in screening_schema.py.
"""

from decimal import Decimal
from django import forms
from .screening_schema import (
    STAGE1_INPUT_SCHEMA,
    SEX_CHOICES,
    HYPERTENSION_CHOICES,
    SMOKING_CHOICES,
    CANONICAL_PREDICTOR_ORDER,
)


class Stage1ScreeningForm(forms.Form):
    """
    Authoritative server-side validation form for Stage-1 non-laboratory screening.
    
    Accepts exclusively the 7 immutable predictors defined in FINAL_MODEL_SPECIFICATION_LOCKED.md.
    No laboratory parameters (HbA1c, glucose) or extraneous clinical variables permitted.
    """

    age = forms.IntegerField(
        label=STAGE1_INPUT_SCHEMA['age']['label'],
        min_value=STAGE1_INPUT_SCHEMA['age']['min_value'],
        max_value=STAGE1_INPUT_SCHEMA['age']['max_value'],
        required=True,
        widget=forms.NumberInput(attrs={
            'class': 'ui-input tabular-nums',
            'placeholder': STAGE1_INPUT_SCHEMA['age']['placeholder'],
            'min': STAGE1_INPUT_SCHEMA['age']['min_value'],
            'max': STAGE1_INPUT_SCHEMA['age']['max_value'],
            'step': 1,
            'aria-describedby': 'id_age_help',
        }),
        error_messages={
            'required': 'Age is required. Enter an age within the model-supported research range (18 to 80 years).',
            'min_value': 'Age is below the model-supported research range (minimum: 18 years).',
            'max_value': 'Age is above the model-supported research range (maximum: 80 years).',
            'invalid': 'Enter a valid whole number for age.',
        }
    )

    sex = forms.ChoiceField(
        label=STAGE1_INPUT_SCHEMA['sex']['label'],
        choices=SEX_CHOICES,
        required=True,
        widget=forms.RadioSelect(attrs={
            'class': 'ui-radio-input',
            'aria-describedby': 'id_sex_help',
        }),
        error_messages={
            'required': 'Biological sex is required. Select Male or Female.',
            'invalid_choice': 'Select a valid choice (Male or Female).',
        }
    )

    height_cm = forms.FloatField(
        label='Height',
        min_value=50.0,
        max_value=250.0,
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'ui-input tabular-nums',
            'placeholder': 'e.g., 170',
            'min': '50.0',
            'max': '250.0',
            'step': '0.1',
            'aria-describedby': 'id_height_cm_help',
        }),
        error_messages={
            'min_value': 'Height is below the valid range (minimum: 50.0 cm).',
            'max_value': 'Height is above the valid range (maximum: 250.0 cm).',
            'invalid': 'Enter a valid numeric height in centimeters.',
        }
    )

    weight_kg = forms.FloatField(
        label='Weight',
        min_value=20.0,
        max_value=350.0,
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'ui-input tabular-nums',
            'placeholder': 'e.g., 70',
            'min': '20.0',
            'max': '350.0',
            'step': '0.1',
            'aria-describedby': 'id_weight_kg_help',
        }),
        error_messages={
            'min_value': 'Weight is below the valid range (minimum: 20.0 kg).',
            'max_value': 'Weight is above the valid range (maximum: 350.0 kg).',
            'invalid': 'Enter a valid numeric weight in kilograms.',
        }
    )

    bmi = forms.FloatField(
        label=STAGE1_INPUT_SCHEMA['bmi']['label'],
        required=False,
        widget=forms.HiddenInput(attrs={
            'id': 'id_bmi',
        }),
    )

    waist_cm = forms.FloatField(
        label=STAGE1_INPUT_SCHEMA['waist_cm']['label'],
        min_value=STAGE1_INPUT_SCHEMA['waist_cm']['min_value'],
        max_value=STAGE1_INPUT_SCHEMA['waist_cm']['max_value'],
        required=True,
        widget=forms.NumberInput(attrs={
            'class': 'ui-input tabular-nums',
            'placeholder': STAGE1_INPUT_SCHEMA['waist_cm']['placeholder'],
            'min': STAGE1_INPUT_SCHEMA['waist_cm']['min_value'],
            'max': STAGE1_INPUT_SCHEMA['waist_cm']['max_value'],
            'step': '0.1',
            'aria-describedby': 'id_waist_cm_help',
        }),
        error_messages={
            'required': 'Waist circumference is required. Enter a measurement between 60.0 and 187.0 cm.',
            'min_value': 'Waist circumference is below the range supported by the research model (minimum: 60.0 cm).',
            'max_value': 'Waist circumference is above the range supported by the research model (maximum: 187.0 cm).',
            'invalid': 'Enter a valid numeric measurement in centimeters (e.g., 98.5).',
        }
    )

    hypertension_history = forms.ChoiceField(
        label=STAGE1_INPUT_SCHEMA['hypertension_history']['label'],
        choices=HYPERTENSION_CHOICES,
        required=True,
        widget=forms.RadioSelect(attrs={
            'class': 'ui-radio-input',
            'aria-describedby': 'id_hypertension_history_help',
        }),
        error_messages={
            'required': 'History of hypertension is required. Select Yes or No.',
            'invalid_choice': 'Select a valid choice (Yes or No).',
        }
    )

    smoking_history = forms.ChoiceField(
        label=STAGE1_INPUT_SCHEMA['smoking_history']['label'],
        choices=SMOKING_CHOICES,
        required=True,
        widget=forms.RadioSelect(attrs={
            'class': 'ui-radio-input',
            'aria-describedby': 'id_smoking_history_help',
        }),
        error_messages={
            'required': 'Smoking history is required. Select Yes or No.',
            'invalid_choice': 'Select a valid choice (Yes or No).',
        }
    )

    sedentary_minutes_day = forms.IntegerField(
        label=STAGE1_INPUT_SCHEMA['sedentary_minutes_day']['label'],
        min_value=STAGE1_INPUT_SCHEMA['sedentary_minutes_day']['min_value'],
        max_value=STAGE1_INPUT_SCHEMA['sedentary_minutes_day']['max_value'],
        required=True,
        widget=forms.NumberInput(attrs={
            'class': 'ui-input tabular-nums',
            'placeholder': STAGE1_INPUT_SCHEMA['sedentary_minutes_day']['placeholder'],
            'min': STAGE1_INPUT_SCHEMA['sedentary_minutes_day']['min_value'],
            'max': STAGE1_INPUT_SCHEMA['sedentary_minutes_day']['max_value'],
            'step': 1,
            'aria-describedby': 'id_sedentary_minutes_day_help',
        }),
        error_messages={
            'required': 'Sedentary time is required. Enter minutes per day (0 to 1200 min/day).',
            'min_value': 'Sedentary time cannot be negative (minimum: 0 minutes/day).',
            'max_value': 'Sedentary time is outside the range supported by the research model (maximum: 1200 minutes/day).',
            'invalid': 'Enter a valid whole number of minutes per day.',
        }
    )

    def clean(self):
        cleaned_data = super().clean()
        height_cm = cleaned_data.get('height_cm')
        weight_kg = cleaned_data.get('weight_kg')
        submitted_bmi = cleaned_data.get('bmi')

        min_bmi = Decimal(str(STAGE1_INPUT_SCHEMA['bmi']['min_value']))
        max_bmi = Decimal(str(STAGE1_INPUT_SCHEMA['bmi']['max_value']))

        # Path 1: Participant intake with height and weight
        if height_cm is not None or weight_kg is not None:
            if height_cm is None:
                self.add_error('height_cm', 'Height is required. Enter height in centimeters.')
            if weight_kg is None:
                self.add_error('weight_kg', 'Weight is required. Enter weight in kilograms.')

            if height_cm is not None and weight_kg is not None:
                if height_cm <= 0:
                    self.add_error('height_cm', 'Height must be greater than zero.')
                elif weight_kg <= 0:
                    self.add_error('weight_kg', 'Weight must be greater than zero.')
                else:
                    # Authoritative independent backend BMI calculation: BMI = weight_kg / (height_m ^ 2)
                    h_m = float(height_cm) / 100.0
                    w_kg = float(weight_kg)
                    calculated_bmi = Decimal(str(round(w_kg / (h_m ** 2), 2)))

                    if calculated_bmi < min_bmi or calculated_bmi > max_bmi:
                        self.add_error(
                            'weight_kg',
                            f'Calculated BMI ({calculated_bmi:.2f} kg/m²) is outside the model-supported research range ({min_bmi} to {max_bmi} kg/m²). Please verify height and weight inputs.'
                        )

                    # Authoritative override: never trust client-submitted BMI
                    cleaned_data['bmi'] = calculated_bmi

        # Path 2: Direct BMI submission (backward compatibility for existing automated test payloads)
        elif submitted_bmi is not None:
            rounded_bmi = Decimal(str(round(float(submitted_bmi), 2)))
            if rounded_bmi < min_bmi or rounded_bmi > max_bmi:
                self.add_error(
                    'bmi',
                    f'This value ({rounded_bmi}) is outside the range supported by the current research model ({min_bmi} to {max_bmi} kg/m²).'
                )
            cleaned_data['bmi'] = rounded_bmi
        else:
            self.add_error('bmi', 'Height and weight are required to calculate BMI.')

        return cleaned_data

    def clean_waist_cm(self):
        """Round waist circumference to 1 decimal place and re-verify bounds."""
        val = self.cleaned_data.get('waist_cm')
        if val is not None:
            val = round(val, 1)
            min_val = STAGE1_INPUT_SCHEMA['waist_cm']['min_value']
            max_val = STAGE1_INPUT_SCHEMA['waist_cm']['max_value']
            if val < min_val or val > max_val:
                raise forms.ValidationError(
                    f'This value ({val}) is outside the range supported by the current research model ({min_val} to {max_val} cm).'
                )
        return val

    def clean_sedentary_minutes_day(self):
        """Reject NHANES sentinel missing codes (7777, 9999) and enforce valid range."""
        val = self.cleaned_data.get('sedentary_minutes_day')
        if val is not None:
            if val in [7777, 9999]:
                raise forms.ValidationError(
                    'This value is outside the range supported by the current research model (0 to 1200 minutes/day).'
                )
            if val < 0 or val > 1200:
                raise forms.ValidationError(
                    'This value is outside the range supported by the current research model (0 to 1200 minutes/day).'
                )
        return val

    def get_sanitized_summary(self):
        """
        Produce a human-readable summary dictionary for the Input Review State.
        Does NOT execute model inference or compute probabilities.
        """
        if not self.is_valid():
            return None

        cd = self.cleaned_data
        sex_display = dict(SEX_CHOICES).get(cd['sex'], cd['sex'])
        hyp_display = dict(HYPERTENSION_CHOICES).get(cd['hypertension_history'], cd['hypertension_history'])
        smk_display = dict(SMOKING_CHOICES).get(cd['smoking_history'], cd['smoking_history'])

        summary = [
            {
                'canonical_name': 'age',
                'label': STAGE1_INPUT_SCHEMA['age']['label'],
                'value': cd['age'],
                'display_value': f"{cd['age']} years",
                'unit': STAGE1_INPUT_SCHEMA['age']['unit'],
                'section': STAGE1_INPUT_SCHEMA['age']['section_title'],
            },
            {
                'canonical_name': 'sex',
                'label': STAGE1_INPUT_SCHEMA['sex']['label'],
                'value': cd['sex'],
                'display_value': sex_display,
                'unit': None,
                'section': STAGE1_INPUT_SCHEMA['sex']['section_title'],
            },
        ]
        if cd.get('height_cm') is not None:
            summary.append({
                'canonical_name': 'height_cm',
                'label': 'Height',
                'value': cd['height_cm'],
                'display_value': f"{cd['height_cm']:.1f} cm",
                'unit': 'cm',
                'section': '2. Body Measurements',
            })
        if cd.get('weight_kg') is not None:
            summary.append({
                'canonical_name': 'weight_kg',
                'label': 'Weight',
                'value': cd['weight_kg'],
                'display_value': f"{cd['weight_kg']:.1f} kg",
                'unit': 'kg',
                'section': '2. Body Measurements',
            })

        # When height_cm is present, display calculated BMI formatted to 2 decimal places
        # For legacy direct-BMI payloads, preserve the original value format
        if cd.get('height_cm') is not None:
            bmi_display_str = f"{cd['bmi']:.2f} kg/m²"
        else:
            bmi_display_str = f"{cd['bmi']} kg/m²"

        summary.extend([
            {
                'canonical_name': 'bmi',
                'label': STAGE1_INPUT_SCHEMA['bmi']['label'],
                'value': cd['bmi'],
                'display_value': bmi_display_str,
                'unit': STAGE1_INPUT_SCHEMA['bmi']['unit'],
                'section': STAGE1_INPUT_SCHEMA['bmi']['section_title'],
            },
            {
                'canonical_name': 'waist_cm',
                'label': STAGE1_INPUT_SCHEMA['waist_cm']['label'],
                'value': cd['waist_cm'],
                'display_value': f"{cd['waist_cm']:.1f} cm",
                'unit': STAGE1_INPUT_SCHEMA['waist_cm']['unit'],
                'section': STAGE1_INPUT_SCHEMA['waist_cm']['section_title'],
            },
            {
                'canonical_name': 'hypertension_history',
                'label': STAGE1_INPUT_SCHEMA['hypertension_history']['label'],
                'value': cd['hypertension_history'],
                'display_value': hyp_display,
                'unit': None,
                'section': STAGE1_INPUT_SCHEMA['hypertension_history']['section_title'],
            },
            {
                'canonical_name': 'smoking_history',
                'label': STAGE1_INPUT_SCHEMA['smoking_history']['label'],
                'value': cd['smoking_history'],
                'display_value': smk_display,
                'unit': None,
                'section': STAGE1_INPUT_SCHEMA['smoking_history']['section_title'],
            },
            {
                'canonical_name': 'sedentary_minutes_day',
                'label': STAGE1_INPUT_SCHEMA['sedentary_minutes_day']['label'],
                'value': cd['sedentary_minutes_day'],
                'display_value': f"{cd['sedentary_minutes_day']} minutes/day",
                'unit': STAGE1_INPUT_SCHEMA['sedentary_minutes_day']['unit'],
                'section': STAGE1_INPUT_SCHEMA['sedentary_minutes_day']['section_title'],
            },
        ])
        return summary


import re
from .models import (
    OVERRIDE_REASONS_REFER_TO_NO_REFER,
    OVERRIDE_REASONS_NO_REFER_TO_REFER,
    ALL_OVERRIDE_REASONS_DICT,
)


class HumanReviewAcceptForm(forms.Form):
    """
    Form validating submission of a human review acceptance.
    Collects strictly the anonymous Reviewer Code.
    The system requests a pseudonymous reviewer code and does not require
    personally identifying information.
    """
    reviewer_code = forms.CharField(
        max_length=32,
        min_length=1,
        strip=True,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'ui-input',
            'placeholder': 'e.g. R001, HP-03',
            'id': 'reviewer-code-input',
            'maxlength': '32',
            'autocomplete': 'off',
            'aria-describedby': 'reviewer-code-help',
        }),
        error_messages={
            'required': 'Enter your reviewer code before submitting this review.',
            'max_length': 'Reviewer code must be 32 characters or fewer.',
        }
    )

    def clean_reviewer_code(self):
        code = self.cleaned_data.get('reviewer_code', '').strip()
        if not code:
            raise forms.ValidationError('Enter your reviewer code before submitting this review.')
        if not re.match(r'^[a-zA-Z0-9_-]+$', code):
            raise forms.ValidationError('Reviewer code may contain only letters, numbers, hyphens, and underscores.')
        return code


class HumanReviewOverrideForm(forms.Form):
    """
    Form validating submission of a human review override.
    Enforces:
    1. Valid pseudonymous reviewer code (max 32 chars).
    2. Branch-specific structured reason code.
    3. Mandatory note if 'other' reason code is selected.
    4. Maximum 500 characters for contextual note.
    Does NOT collect personal identity, medical credentials, or clinical diagnoses.
    """
    reviewer_code = forms.CharField(
        max_length=32,
        min_length=1,
        strip=True,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'ui-input',
            'placeholder': 'e.g. R001, HP-03',
            'id': 'override-reviewer-code-input',
            'maxlength': '32',
            'autocomplete': 'off',
            'aria-describedby': 'override-reviewer-code-help',
        }),
        error_messages={
            'required': 'Enter your reviewer code before submitting this override.',
            'max_length': 'Reviewer code must be 32 characters or fewer.',
        }
    )
    override_reason_code = forms.CharField(
        max_length=64,
        required=True,
        error_messages={
            'required': 'Please select a reason for the override.',
        }
    )
    override_note = forms.CharField(
        max_length=500,
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'ui-input',
            'id': 'override-note-input',
            'rows': 3,
            'maxlength': '500',
            'placeholder': 'Optional brief contextual rationale (max 500 characters)...',
            'aria-describedby': 'override-note-help',
        }),
        error_messages={
            'max_length': 'Note must be 500 characters or fewer.',
        }
    )

    def __init__(self, *args, ai_referral_recommended=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.ai_referral_recommended = ai_referral_recommended
        if ai_referral_recommended is True:
            self.fields['override_reason_code'].choices = OVERRIDE_REASONS_REFER_TO_NO_REFER
        elif ai_referral_recommended is False:
            self.fields['override_reason_code'].choices = OVERRIDE_REASONS_NO_REFER_TO_REFER
        else:
            self.fields['override_reason_code'].choices = list(ALL_OVERRIDE_REASONS_DICT.items())

    def clean_reviewer_code(self):
        code = self.cleaned_data.get('reviewer_code', '').strip()
        if not code:
            raise forms.ValidationError('Enter your reviewer code before submitting this override.')
        if not re.match(r'^[a-zA-Z0-9_-]+$', code):
            raise forms.ValidationError('Reviewer code may contain only letters, numbers, hyphens, and underscores.')
        return code

    def clean_override_reason_code(self):
        code = self.cleaned_data.get('override_reason_code', '').strip()
        if not code:
            raise forms.ValidationError('Please select a reason for the override.')
        if self.ai_referral_recommended is True:
            valid_codes = [c[0] for c in OVERRIDE_REASONS_REFER_TO_NO_REFER]
            if code not in valid_codes:
                raise forms.ValidationError('Selected reason is invalid for a Refer to Do Not Refer override.')
        elif self.ai_referral_recommended is False:
            valid_codes = [c[0] for c in OVERRIDE_REASONS_NO_REFER_TO_REFER]
            if code not in valid_codes:
                raise forms.ValidationError('Selected reason is invalid for a Do Not Refer to Refer override.')
        return code

    def clean(self):
        cleaned_data = super().clean()
        reason = cleaned_data.get('override_reason_code')
        note = cleaned_data.get('override_note', '')
        note_stripped = note.strip() if note else ''
        cleaned_data['override_note'] = note_stripped

        if reason == 'other' and not note_stripped:
            self.add_error('override_note', 'Provide a short reason when selecting Other.')

        return cleaned_data


class UnifiedHumanReviewForm(forms.Form):
    """
    Unified form for submitting a human review decision (Accept or Override).
    Captures the decision, reviewer code, structured override factor / learning signal,
    and optional contextual rationale in a single, unified review action.

    The Human Override itself is the intervention that generates the learning feedback.
    """
    reviewer_code = forms.CharField(
        max_length=32,
        min_length=1,
        strip=True,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'ui-input',
            'placeholder': 'e.g. R001, HP-03',
            'id': 'unified-reviewer-code-input',
            'maxlength': '32',
            'autocomplete': 'off',
            'aria-describedby': 'unified-reviewer-code-help',
        }),
        error_messages={
            'required': 'Enter your reviewer code before submitting this review.',
            'max_length': 'Reviewer code must be 32 characters or fewer.',
        }
    )
    human_decision = forms.ChoiceField(
        choices=[
            ('accept', 'Accept AI Recommendation'),
            ('override', 'Override AI Recommendation'),
        ],
        required=True,
        widget=forms.RadioSelect(attrs={'class': 'ui-radio-input'}),
        error_messages={
            'required': 'Select whether to accept or override the AI recommendation.',
        }
    )
    override_factor = forms.ChoiceField(
        required=False,
        widget=forms.Select(attrs={
            'class': 'ui-select',
            'id': 'unified-override-factor-select',
        }),
    )
    target_feature = forms.CharField(
        max_length=32,
        required=False,
        widget=forms.HiddenInput(attrs={'id': 'feedback-lab-target-input'}),
    )
    signal_direction = forms.CharField(
        max_length=20,
        required=False,
    )
    signal_scope = forms.CharField(
        max_length=32,
        required=False,
        widget=forms.HiddenInput(attrs={'id': 'feedback-lab-scope-input'}),
    )
    rationale = forms.CharField(
        max_length=500,
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'ui-input',
            'id': 'unified-rationale-input',
            'rows': 3,
            'maxlength': '500',
            'placeholder': 'Optional brief decision rationale (max 500 characters)...',
            'aria-describedby': 'unified-rationale-help',
        }),
        error_messages={
            'max_length': 'Rationale must be 500 characters or fewer.',
        }
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from .services.feedback_taxonomy import OVERRIDE_FACTOR_CHOICES
        self.fields['override_factor'].choices = [
            ('', '-- Select Override Factor / Learning Signal --')
        ] + list(OVERRIDE_FACTOR_CHOICES)

    def clean_reviewer_code(self):
        code = self.cleaned_data.get('reviewer_code', '').strip()
        if not code:
            raise forms.ValidationError('Enter your reviewer code before submitting this review.')
        if not re.match(r'^[a-zA-Z0-9_-]+$', code):
            raise forms.ValidationError('Reviewer code may contain only letters, numbers, hyphens, and underscores.')
        return code

    def clean(self):
        cleaned_data = super().clean()
        decision = cleaned_data.get('human_decision')
        factor = cleaned_data.get('override_factor')
        rationale = (cleaned_data.get('rationale') or '').strip()
        cleaned_data['rationale'] = rationale

        if decision == 'override':
            if not factor:
                self.add_error('override_factor', 'Please select an override factor / learning signal.')
            elif factor == 'other' and not rationale:
                self.add_error('rationale', 'Provide a brief explanation when selecting Other.')

            target_feat = cleaned_data.get('target_feature')
            sig_dir = cleaned_data.get('signal_direction')
            if factor == 'no_learning_signal' or target_feat == 'none':
                if sig_dir and sig_dir not in ('none', ''):
                    self.add_error(
                        'signal_direction',
                        'No learning signal cannot be combined with directional adjustments (reduce/increase).'
                    )
                else:
                    cleaned_data['signal_direction'] = 'none'
                    cleaned_data['signal_scope'] = 'none'
                    cleaned_data['target_feature'] = 'none'
        elif decision == 'accept':
            if not factor:
                cleaned_data['override_factor'] = 'no_learning_signal'
            cleaned_data['signal_direction'] = 'none'
            cleaned_data['signal_scope'] = 'none'
            cleaned_data['target_feature'] = 'none'

        return cleaned_data


class Stage2EntryForm(forms.Form):
    """
    Initial input form for Stage-2 HbA1c laboratory assessment.
    
    Accepts solely an HbA1c percentage value.
    Does NOT accept glucose, OGTT, diagnosis, or range overrides.
    """
    hba1c_percent = forms.DecimalField(
        label="HbA1c Laboratory Value",
        min_value=Decimal("2.0"),
        max_value=Decimal("25.0"),
        max_digits=4,
        decimal_places=2,
        required=True,
        widget=forms.NumberInput(attrs={
            'class': 'ui-input tabular-nums',
            'placeholder': 'e.g. 5.70, 6.10, 6.50',
            'step': '0.01',
            'min': '2.00',
            'max': '25.00',
            'id': 'hba1c-input',
            'aria-describedby': 'hba1c-help',
            'autocomplete': 'off',
        }),
        error_messages={
            'required': 'Enter an HbA1c percentage to proceed with Stage-2 assessment.',
            'invalid': 'Enter a valid numeric percentage for HbA1c (e.g. 6.10).',
            'min_value': 'HbA1c must be at least 2.0%.',
            'max_value': 'HbA1c value exceeds practical input safety bound (maximum: 25.0%).',
        }
    )


class HumanFeedbackForm(forms.Form):
    """
    Form for submitting structured human feedback on a screening prediction.

    The human-selected structured category is the CANONICAL learning signal.
    Optional free-text is processed by NLP but never directly becomes the training target.

    GOVERNANCE:
    - Does NOT modify the original ScreeningRecord or its AI prediction.
    - Does NOT directly modify model weights.
    - The structured category must exist in the master feedback taxonomy.
    """
    structured_category = forms.CharField(
        max_length=64,
        required=True,
        error_messages={
            'required': 'Please select a feedback category.',
        }
    )
    feedback_text = forms.CharField(
        max_length=2000,
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'ui-input',
            'id': 'feedback-text-input',
            'rows': 3,
            'maxlength': '2000',
            'placeholder': 'Optional: describe why you believe the model assessment could be improved for similar cases...',
            'aria-describedby': 'feedback-text-help',
        }),
        error_messages={
            'max_length': 'Feedback text must be 2000 characters or fewer.',
        }
    )

    def clean_structured_category(self):
        from .services.feedback_taxonomy import validate_category_id, get_category, DIR_NO_LEARNING
        category_id = self.cleaned_data.get('structured_category', '').strip()
        if not category_id:
            raise forms.ValidationError('Please select a feedback category.')
        if not validate_category_id(category_id):
            raise forms.ValidationError(f"'{category_id}' is not a valid feedback category.")
        return category_id
class Stage2ConfirmForm(forms.Form):
    """
    Confirmation form for Stage-2 HbA1c persistence.
    
    Revalidates the submitted HbA1c value server-side.
    Client-injected fields (e.g. laboratory_range, diagnosis) are ignored.
    """
    hba1c_percent = forms.DecimalField(
        min_value=Decimal("2.0"),
        max_value=Decimal("25.0"),
        max_digits=4,
        decimal_places=2,
        required=True,
        widget=forms.HiddenInput(),
        error_messages={
            'required': 'HbA1c percentage is required for confirmation.',
            'invalid': 'Invalid HbA1c percentage.',
            'min_value': 'HbA1c must be at least 2.0%.',
            'max_value': 'HbA1c value exceeds practical input safety bound (maximum: 25.0%).',
        }
    )


class EvaluationConsentForm(forms.Form):
    """
    Informed Consent and Demographic Intake Form for Evaluation Participants.
    Protocol E1 v1.0.3 / E2 Implementation.
    """
    AGE_CHOICES = [
        ('', '-- Pilih Kelompok Usia --'),
        ('18-24', '18–24 tahun'),
        ('25-34', '25–34 tahun'),
        ('35-44', '35–44 tahun'),
        ('45-54', '45–54 tahun'),
        ('55+', '55 tahun ke atas'),
    ]
    EDUCATION_CHOICES = [
        ('', '-- Pilih Pendidikan Terakhir --'),
        ('sma_smk', 'SMA / SMK Sederajat'),
        ('diploma', 'Diploma (D3 / D4)'),
        ('sarjana', 'Sarjana (S1)'),
        ('magister', 'Magister (S2)'),
        ('doktoral', 'Doktoral (S3)'),
    ]
    TECHNICAL_CHOICES = [
        ('', '-- Pilih Latar Belakang Teknis --'),
        ('non_technical', 'Non-Teknis (Pengguna umum komputer/ponsel)'),
        ('intermediate', 'Menengah (Terbiasa menggunakan aplikasi analitik/data)'),
        ('technical', 'Teknis (Latar belakang TI, rekayasa perangkat lunak, atau data science)'),
    ]
    HEALTH_CHOICES = [
        ('', '-- Pilih Latar Belakang Kesehatan --'),
        ('layperson', 'Bukan Tenaga Kesehatan (Masyarakat umum / non-medis)'),
        ('student', 'Mahasiswa Bidang Kesehatan / Kedokteran'),
        ('professional', 'Tenaga Kesehatan Profesional (Dokter, perawat, analis lab, dsb.)'),
    ]

    age_group = forms.ChoiceField(
        label="Kelompok Usia",
        choices=AGE_CHOICES,
        required=True,
        widget=forms.Select(attrs={'class': 'ui-select', 'id': 'id_age_group'}),
        error_messages={'required': 'Silakan pilih kelompok usia Anda.'}
    )
    education_level = forms.ChoiceField(
        label="Pendidikan Terakhir",
        choices=EDUCATION_CHOICES,
        required=True,
        widget=forms.Select(attrs={'class': 'ui-select', 'id': 'id_education_level'}),
        error_messages={'required': 'Silakan pilih tingkat pendidikan terakhir Anda.'}
    )
    technical_background = forms.ChoiceField(
        label="Latar Belakang Teknis / Komputasi",
        choices=TECHNICAL_CHOICES,
        required=True,
        widget=forms.Select(attrs={'class': 'ui-select', 'id': 'id_technical_background'}),
        error_messages={'required': 'Silakan pilih latar belakang teknis Anda.'}
    )
    health_background = forms.ChoiceField(
        label="Latar Belakang Bidang Kesehatan",
        choices=HEALTH_CHOICES,
        required=True,
        widget=forms.Select(attrs={'class': 'ui-select', 'id': 'id_health_background'}),
        error_messages={'required': 'Silakan pilih latar belakang kesehatan Anda.'}
    )
    consent_given = forms.BooleanField(
        label="Pernyataan Persetujuan Partisipasi (Informed Consent)",
        required=True,
        widget=forms.CheckboxInput(attrs={'class': 'ui-checkbox', 'id': 'id_consent_given'}),
        error_messages={'required': 'Anda harus menyetujui pernyataan partisipasi sukarela untuk melanjutkan.'}
    )


class DashboardQuestionnaireForm(forms.Form):
    """
    Post-Task Evaluation Questionnaire Form.
    Comprises:
    - Section A: 8 Objective Comprehension Items (C1–C8)
    - Section B: 10 Indonesian SUS Items (Likert 1–5, Sharfina & Santoso 2016)
    - Section C: 5 Dashboard Clarity Items (Likert 1–5)
    - Section D: 3 Qualitative Feedback Items (Open text)
    """
    LIKERT_CHOICES = [
        (1, '1 — Sangat Tidak Setuju'),
        (2, '2 — Tidak Setuju'),
        (3, '3 — Netral'),
        (4, '4 — Setuju'),
        (5, '5 — Sangat Setuju'),
    ]

    # Section A: Comprehension C1–C8
    c1 = forms.ChoiceField(
        label="C1. Nilai probabilitas pada hasil screening AI",
        choices=[('A', 'A. Kepastian bahwa seseorang mengalami diabetes'),
                 ('B', 'B. Perkiraan model berdasarkan data input yang diberikan'),
                 ('C', 'C. Hasil pemeriksaan HbA1c'),
                 ('D', 'D. Keputusan akhir yang wajib diikuti pengguna')],
        widget=forms.RadioSelect(attrs={'class': 'ui-radio-input'}),
        required=True,
    )
    c2 = forms.ChoiceField(
        label="C2. Arti rekomendasi \"REFER\" pada Stage 1",
        choices=[('A', 'A. Sistem memastikan pengguna mengalami diabetes'),
                 ('B', 'B. Sistem menyarankan pemeriksaan lanjutan berdasarkan hasil screening'),
                 ('C', 'C. Pengguna harus langsung menjalani pengobatan'),
                 ('D', 'D. HbA1c pengguna sudah pasti berada di atas 6,5%')],
        widget=forms.RadioSelect(attrs={'class': 'ui-radio-input'}),
        required=True,
    )
    c3 = forms.ChoiceField(
        label="C3. Tujuan feature contribution pada penjelasan AI",
        choices=[('A', 'A. Menunjukkan penyebab biologis dari kondisi pengguna'),
                 ('B', 'B. Menunjukkan bagaimana fitur input berkontribusi terhadap output model'),
                 ('C', 'C. Menggantikan hasil pemeriksaan laboratorium'),
                 ('D', 'D. Menentukan diagnosis akhir pengguna')],
        widget=forms.RadioSelect(attrs={'class': 'ui-radio-input'}),
        required=True,
    )
    c4 = forms.ChoiceField(
        label="C4. Kapan Human Override terjadi?",
        choices=[('A', 'A. Ketika model menghasilkan probabilitas 0%'),
                 ('B', 'B. Ketika pengguna mengubah data input'),
                 ('C', 'C. Ketika keputusan akhir manusia berbeda dari rekomendasi AI'),
                 ('D', 'D. Ketika pengguna melihat XAI')],
        widget=forms.RadioSelect(attrs={'class': 'ui-radio-input'}),
        required=True,
    )
    c5 = forms.ChoiceField(
        label="C5. Pemahaman ketidaksesuaian rekomendasi AI vs keputusan manusia",
        choices=[('A', 'A. AI pasti melakukan kesalahan'),
                 ('B', 'B. Manusia pasti melakukan kesalahan'),
                 ('C', 'C. Terjadi ketidaksesuaian antara rekomendasi AI dan keputusan manusia'),
                 ('D', 'D. Sistem otomatis mengubah probabilitas AI')],
        widget=forms.RadioSelect(attrs={'class': 'ui-radio-input'}),
        required=True,
    )
    c6 = forms.ChoiceField(
        label="C6. Tujuan feedback yang diberikan setelah Human Override",
        choices=[('A', 'A. Mengubah nilai HbA1c pengguna'),
                 ('B', 'B. Memberikan sinyal koreksi dari keputusan manusia yang dapat digunakan dalam mekanisme adaptation'),
                 ('C', 'C. Menghapus prediksi AI sebelumnya'),
                 ('D', 'D. Mengubah hasil final-test model')],
        widget=forms.RadioSelect(attrs={'class': 'ui-radio-input'}),
        required=True,
    )
    c7 = forms.ChoiceField(
        label="C7. Kapan pemeriksaan HbA1c pada Stage 2 dilakukan",
        choices=[('A', 'A. Selalu dilakukan setelah Stage 1'),
                 ('B', 'B. Hanya setelah keputusan akhir manusia adalah REFER'),
                 ('C', 'C. Hanya ketika AI memberikan probabilitas 100%'),
                 ('D', 'D. Sebelum Stage 1')],
        widget=forms.RadioSelect(attrs={'class': 'ui-radio-input'}),
        required=True,
    )
    c8 = forms.ChoiceField(
        label="C8. Perbedaan utama Stage 1 dan Stage 2",
        choices=[('A', 'A. Stage 1 menggunakan HbA1c, sedangkan Stage 2 menggunakan data non-laboratorium'),
                 ('B', 'B. Keduanya merupakan diagnosis otomatis'),
                 ('C', 'C. Stage 1 melakukan non-laboratory risk screening, sedangkan Stage 2 menggunakan HbA1c untuk laboratory-range assessment'),
                 ('D', 'D. Stage 2 digunakan untuk melatih ulang GAM-v1')],
        widget=forms.RadioSelect(attrs={'class': 'ui-radio-input'}),
        required=True,
    )

    # Section B: SUS Items (1 to 10)
    sus_1 = forms.TypedChoiceField(label="1. Saya berpikir bahwa saya ingin sering menggunakan sistem ini.", choices=LIKERT_CHOICES, coerce=int, widget=forms.RadioSelect(attrs={'class': 'ui-radio-input'}), required=True)
    sus_2 = forms.TypedChoiceField(label="2. Saya merasa sistem ini rumit untuk digunakan.", choices=LIKERT_CHOICES, coerce=int, widget=forms.RadioSelect(attrs={'class': 'ui-radio-input'}), required=True)
    sus_3 = forms.TypedChoiceField(label="3. Saya merasa sistem ini mudah digunakan.", choices=LIKERT_CHOICES, coerce=int, widget=forms.RadioSelect(attrs={'class': 'ui-radio-input'}), required=True)
    sus_4 = forms.TypedChoiceField(label="4. Saya membutuhkan bantuan dari orang lain atau teknisi dalam menggunakan sistem ini.", choices=LIKERT_CHOICES, coerce=int, widget=forms.RadioSelect(attrs={'class': 'ui-radio-input'}), required=True)
    sus_5 = forms.TypedChoiceField(label="5. Saya merasa fungsi-fungsi dalam sistem ini bekerja dengan baik.", choices=LIKERT_CHOICES, coerce=int, widget=forms.RadioSelect(attrs={'class': 'ui-radio-input'}), required=True)
    sus_6 = forms.TypedChoiceField(label="6. Saya merasa ada banyak hal yang tidak konsisten pada sistem ini.", choices=LIKERT_CHOICES, coerce=int, widget=forms.RadioSelect(attrs={'class': 'ui-radio-input'}), required=True)
    sus_7 = forms.TypedChoiceField(label="7. Saya merasa bahwa orang lain akan memahami cara menggunakan sistem ini dengan cepat.", choices=LIKERT_CHOICES, coerce=int, widget=forms.RadioSelect(attrs={'class': 'ui-radio-input'}), required=True)
    sus_8 = forms.TypedChoiceField(label="8. Saya merasa sistem ini membingungkan.", choices=LIKERT_CHOICES, coerce=int, widget=forms.RadioSelect(attrs={'class': 'ui-radio-input'}), required=True)
    sus_9 = forms.TypedChoiceField(label="9. Saya merasa tidak ada hambatan dalam menggunakan sistem ini.", choices=LIKERT_CHOICES, coerce=int, widget=forms.RadioSelect(attrs={'class': 'ui-radio-input'}), required=True)
    sus_10 = forms.TypedChoiceField(label="10. Saya perlu membiasakan diri terlebih dahulu sebelum menggunakan sistem ini.", choices=LIKERT_CHOICES, coerce=int, widget=forms.RadioSelect(attrs={'class': 'ui-radio-input'}), required=True)

    # Section C: Dashboard Clarity Items (DQ1 to DQ5)
    clarity_1 = forms.TypedChoiceField(label="DQ1. Informasi yang ditampilkan pada dashboard mudah saya pahami.", choices=LIKERT_CHOICES, coerce=int, widget=forms.RadioSelect(attrs={'class': 'ui-radio-input'}), required=True)
    clarity_2 = forms.TypedChoiceField(label="DQ2. Penjelasan feature contribution membantu saya memahami hasil AI.", choices=LIKERT_CHOICES, coerce=int, widget=forms.RadioSelect(attrs={'class': 'ui-radio-input'}), required=True)
    clarity_3 = forms.TypedChoiceField(label="DQ3. Perbedaan antara rekomendasi AI dan keputusan manusia mudah saya pahami.", choices=LIKERT_CHOICES, coerce=int, widget=forms.RadioSelect(attrs={'class': 'ui-radio-input'}), required=True)
    clarity_4 = forms.TypedChoiceField(label="DQ4. Mekanisme Human Override mudah saya pahami.", choices=LIKERT_CHOICES, coerce=int, widget=forms.RadioSelect(attrs={'class': 'ui-radio-input'}), required=True)
    clarity_5 = forms.TypedChoiceField(label="DQ5. Alur dari Stage 1 ke Stage 2 mudah saya pahami.", choices=LIKERT_CHOICES, coerce=int, widget=forms.RadioSelect(attrs={'class': 'ui-radio-input'}), required=True)

    # Section D: Qualitative Feedback Items (OQ1 to OQ3)
    open_1 = forms.CharField(
        label="OQ1. Bagian mana dari dashboard yang paling membantu Anda memahami hasil screening? Jelaskan alasannya.",
        widget=forms.Textarea(attrs={'class': 'ui-input', 'rows': 3, 'placeholder': 'Tuliskan tanggapan Anda di sini (opsional)...'}),
        required=False,
    )
    open_2 = forms.CharField(
        label="OQ2. Bagian mana dari dashboard yang menurut Anda paling membingungkan atau sulit dipahami?",
        widget=forms.Textarea(attrs={'class': 'ui-input', 'rows': 3, 'placeholder': 'Tuliskan tanggapan Anda di sini (opsional)...'}),
        required=False,
    )
    open_3 = forms.CharField(
        label="OQ3. Apa perbaikan utama yang menurut Anda dapat membuat dashboard ini lebih mudah dipahami atau digunakan?",
        widget=forms.Textarea(attrs={'class': 'ui-input', 'rows': 3, 'placeholder': 'Tuliskan tanggapan Anda di sini (opsional)...'}),
        required=False,
    )


