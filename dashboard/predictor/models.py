from django.db import models
from django.core.exceptions import ValidationError
import json


class Prediction(models.Model):
    """
    Stores every AI prediction made through the dashboard.
    Each record captures the patient data, model used, prediction result,
    confidence level, and SHAP explanation values.
    """
    timestamp = models.DateTimeField(auto_now_add=True)
    
    # Patient data stored as JSON (all 8 features)
    patient_data = models.JSONField(
        help_text="JSON object with keys: gender, age, hypertension, heart_disease, smoking, bmi, HbA1c, glucose"
    )
    
    # Which model variant was used for this prediction
    model_used = models.CharField(
        max_length=100,
        help_text="Name of the model used (e.g., 'DLNN Baseline', 'DLNN + Focal Loss')"
    )
    
    # Model output
    prediction = models.IntegerField(
        help_text="Binary prediction: 0 = Not Diabetic, 1 = Diabetic"
    )
    confidence = models.FloatField(
        help_text="Model confidence (probability), 0.0 to 1.0"
    )
    threshold = models.FloatField(
        default=0.5,
        help_text="Classification threshold used for this prediction"
    )
    
    # SHAP explanation values stored as JSON
    shap_values = models.JSONField(
        null=True, blank=True,
        help_text="Per-feature SHAP contribution values as JSON"
    )
    
    # Whether a doctor has reviewed this prediction
    is_reviewed = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        status = "Diabetic" if self.prediction == 1 else "Not Diabetic"
        return f"Prediction #{self.id} - {status} ({self.confidence:.1%}) - {self.model_used}"
    
    def get_patient_data_display(self):
        """Return patient data in a human-readable format."""
        data = self.patient_data
        gender_map = {0: 'Female', 1: 'Male', 2: 'Other'}
        smoking_map = {0: 'Never', 1: 'Former', 2: 'Current', 3: 'Not Current', 4: 'Ever', 5: 'No Info'}
        
        return {
            'Gender': gender_map.get(data.get('gender', -1), 'Unknown'),
            'Age': data.get('age', 'N/A'),
            'Hypertension': 'Yes' if data.get('hypertension') == 1 else 'No',
            'Heart Disease': 'Yes' if data.get('heart_disease') == 1 else 'No',
            'Smoking': smoking_map.get(data.get('smoking', -1), 'Unknown'),
            'BMI': data.get('bmi', 'N/A'),
            'HbA1c': data.get('HbA1c', 'N/A'),
            'Glucose': data.get('glucose', 'N/A'),
        }


class Override(models.Model):
    """
    Stores every doctor decision (accept/reject/override) on an AI prediction.
    This creates an audit trail and provides feedback data for future model improvement.
    """
    DECISION_CHOICES = [
        ('accept', 'Accept'),
        ('reject', 'Reject'),
    ]
    
    prediction = models.ForeignKey(
        Prediction,
        on_delete=models.CASCADE,
        related_name='overrides',
        help_text="The prediction this override relates to"
    )
    
    timestamp = models.DateTimeField(auto_now_add=True)
    
    doctor_name = models.CharField(
        max_length=200,
        help_text="Name of the reviewing doctor/expert"
    )
    
    decision = models.CharField(
        max_length=10,
        choices=DECISION_CHOICES,
        help_text="Doctor's decision: accept or reject the AI prediction"
    )
    
    override_value = models.IntegerField(
        null=True, blank=True,
        help_text="If rejected, the doctor's corrected prediction (0 or 1)"
    )
    
    reason = models.TextField(
        blank=True,
        help_text="Doctor's reason for their decision (required for rejections)"
    )
    
    # Which features the doctor disagrees with
    flagged_features = models.JSONField(
        null=True, blank=True,
        help_text="List of feature names the doctor flagged as unreliable/incorrect"
    )
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"Override #{self.id} - {self.decision} by {self.doctor_name}"


import uuid
from decimal import Decimal


class ScreeningRecord(models.Model):
    """
    Immutable historical record of a Stage-1 non-laboratory screening event.
    Captures:
    1. Identity: UUID primary key (non-sequential, privacy preserving).
    2. Inputs: All 7 canonical non-laboratory predictors stored in human-readable semantics.
    3. Original AI Output: Full precision probability, binary referral recommendation, frozen threshold (0.1389).
    4. Model Provenance: Model name, SHA256 hashes of model and preprocessor artifacts, input schema version.
    5. Audit & Timestamp: Execution timestamp and optional idempotency token.
    
    GOVERNANCE CONSTRAINTS:
    - This record is IMMUTABLE once written.
    - Future Human Review/Override MUST NOT overwrite fields in this record.
    - Does NOT contain clinical diagnosis fields or personal identifiers.
    """
    SEX_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
    ]
    
    BINARY_HISTORY_CHOICES = [
        ('yes', 'Yes'),
        ('no', 'No'),
    ]
    
    # 1. Identity
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique anonymous screening record identifier (UUIDv4)"
    )
    
    # 2. Stage-1 Non-Laboratory Inputs (Human-readable semantic format)
    age = models.PositiveSmallIntegerField(
        help_text="Participant age in years (18 to 80)"
    )
    sex = models.CharField(
        max_length=10,
        choices=SEX_CHOICES,
        help_text="Biological sex (male or female)"
    )
    bmi = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="Body Mass Index in kg/m² (11.1 to 69.9)"
    )
    waist_cm = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        help_text="Waist circumference in cm (60.0 to 187.0)"
    )
    hypertension_history = models.CharField(
        max_length=5,
        choices=BINARY_HISTORY_CHOICES,
        help_text="Doctor-diagnosed hypertension history (yes or no)"
    )
    smoking_history = models.CharField(
        max_length=5,
        choices=BINARY_HISTORY_CHOICES,
        help_text="Smoking history: ≥100 cigarettes lifetime (yes or no)"
    )
    sedentary_minutes_day = models.PositiveSmallIntegerField(
        help_text="Typical daily sedentary time in minutes/day (0 to 1200)"
    )
    
    # 3. Model Output (Original AI Output - Immutable)
    screening_probability = models.FloatField(
        help_text="Stage-1 screening probability at full 64-bit precision (0.0 to 1.0)"
    )
    ai_referral_recommended = models.BooleanField(
        help_text="True if screening_probability >= decision_threshold (0.1389)"
    )
    decision_threshold = models.DecimalField(
        max_digits=6,
        decimal_places=4,
        default=Decimal('0.1389'),
        help_text="Locked research decision threshold (0.1389)"
    )
    
    # 4. Model Provenance
    model_name = models.CharField(
        max_length=100,
        default="Phase-5 GAM (λ=10.0, Splines=10)",
        help_text="Canonical model specification name"
    )
    model_sha256 = models.CharField(
        max_length=64,
        default="204a94ff072ef4f1edecebf5a643738c006bbf010f3817b4bb798d3ea6fef41d",
        help_text="SHA-256 checksum of gam_final.pkl"
    )
    preprocessor_sha256 = models.CharField(
        max_length=64,
        default="6e56a01993a4a6971eb62c82699c49da6f31a3acec2a1169e07862409f42824d",
        help_text="SHA-256 checksum of preprocessor.pkl"
    )
    input_schema_version = models.CharField(
        max_length=20,
        default="1.0",
        help_text="Version of Stage-1 input schema contract"
    )
    
    # 5. Audit & Protection
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp of screening record creation"
    )
    idempotency_token = models.CharField(
        max_length=64,
        unique=True,
        null=True,
        blank=True,
        help_text="Token preventing accidental duplicate submission"
    )
    is_practice = models.BooleanField(
        default=False,
        help_text="True if record is from onboarding practice case P0 (excluded from research analysis and learning)"
    )
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['idempotency_token']),
        ]
        
    def __str__(self):
        signal = "Elevated" if self.ai_referral_recommended else "Lower"
        return f"ScreeningRecord {str(self.id)[:8]}... — {signal} ({self.screening_probability:.1%})"
        
    @property
    def formatted_probability(self) -> str:
        """Formatted display percentage (e.g. '24.7%'). Not used for classification."""
        return f"{self.screening_probability * 100.0:.1f}%"
        
    @property
    def primary_status_label(self) -> str:
        return "Elevated screening signal" if self.ai_referral_recommended else "Lower screening signal"
        
    @property
    def ai_recommendation_text(self) -> str:
        if self.ai_referral_recommended:
            return "Referral for Stage-2 HbA1c assessment is recommended."
        return "The screening model does not recommend referral for Stage-2 HbA1c assessment at the current research operating point."
        
    @property
    def interpretation_text(self) -> str:
        if self.ai_referral_recommended:
            return (
                "The model identified a screening signal above the pre-specified research operating point. "
                "Stage-2 HbA1c assessment is recommended for further laboratory evaluation."
            )
        return (
            "The model did not identify a screening signal above the pre-specified research operating point. "
            "A lower screening signal does not rule out dysglycemia. This result reflects the screening model's "
            "recommendation at the pre-specified research operating point."
        )


class ScreeningExplanation(models.Model):
    """
    Stores an immutable, auditable, GAM-native additive explanation
    for a Stage-1 ScreeningRecord.
    Answers: 'Why did the frozen GAM produce this screening result?'
    Strictly non-causal. No legacy SHAP.
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique explanation record identifier (UUIDv4)"
    )
    screening_record = models.OneToOneField(
        'ScreeningRecord',
        on_delete=models.CASCADE,
        related_name='explanation',
        help_text="Parent screening record explained by this decomposition"
    )
    method = models.CharField(
        max_length=50,
        default="gam_native_additive",
        help_text="Method used for explanation ('gam_native_additive')"
    )
    method_version = models.CharField(
        max_length=20,
        default="1.0",
        help_text="Version of explanation method contract"
    )
    link_function = models.CharField(
        max_length=20,
        default="logit",
        help_text="Link function on which additive terms are defined ('logit')"
    )
    intercept = models.FloatField(
        help_text="Frozen GAM model intercept (β0) on logit scale"
    )
    contributions_json = models.JSONField(
        help_text="JSON list of 7 feature contribution dicts"
    )
    reconstructed_linear_predictor = models.FloatField(
        help_text="Reconstructed sum of intercept and all feature contributions (η_recon)"
    )
    reconstructed_probability = models.FloatField(
        help_text="Reconstructed screening probability via inverse logit: σ(η_recon)"
    )
    reconstruction_error = models.FloatField(
        help_text="Absolute reconstruction error: |reconstructed_probability - screening_probability|"
    )
    model_sha256 = models.CharField(
        max_length=64,
        default="204a94ff072ef4f1edecebf5a643738c006bbf010f3817b4bb798d3ea6fef41d",
        help_text="SHA-256 checksum of gam_final.pkl at explanation time"
    )
    status = models.CharField(
        max_length=20,
        choices=[
            ('generated', 'Generated'),
            ('failed', 'Failed'),
        ],
        default='generated',
        help_text="Explanation generation status"
    )
    failure_reason = models.TextField(
        blank=True,
        default="",
        help_text="Failure diagnostic if status == 'failed'"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp of explanation creation"
    )

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"ScreeningExplanation for {str(self.screening_record_id)[:8]}... ({self.status})"


class HumanReview(models.Model):
    """
    Audit record of a human review performed on an immutable Stage-1 ScreeningRecord.
    Captures:
    1. Identity: UUID primary key (non-sequential, privacy preserving).
    2. Relation: OneToOneField to ScreeningRecord (at most one finalized review per screening).
    3. Reviewer Code: Anonymous study-safe identifier (max 32 chars, no PII).
    4. Review Action: For D2.6, strictly 'accepted' (accepting the AI referral recommendation).
    5. Final Decision: Derived server-side from screening_record.ai_referral_recommended.
    6. Audit Timestamp: Timestamp of review submission.

    GOVERNANCE CONSTRAINTS:
    - This record is IMMUTABLE once written from normal end-user UI.
    - Operates on the AI Referral Recommendation, NOT biological diagnosis.
    - Acceptance signifies decision concordance, NOT ground-truth model accuracy.
    - Override signifies decision disagreement and records structured rationale.
    - Does NOT contain clinical diagnosis, disease class flipping, or HbA1c values.
    """
    ACTION_CHOICES = [
        ('accepted', 'Accepted Recommendation'),
        ('overridden', 'Overridden Recommendation'),
    ]

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique anonymous review identifier (UUIDv4)"
    )
    screening_record = models.OneToOneField(
        'ScreeningRecord',
        on_delete=models.PROTECT,
        related_name='human_review',
        help_text="Parent screening record reviewed"
    )
    reviewer_code = models.CharField(
        max_length=32,
        help_text="Anonymous study-safe reviewer identifier (e.g. R001, HP-03)"
    )
    review_action = models.CharField(
        max_length=20,
        choices=ACTION_CHOICES,
        help_text="Reviewer action: explicitly 'accepted' or 'overridden'"
    )
    final_referral_recommended = models.BooleanField(
        help_text="Final referral decision derived server-side"
    )
    override_reason_code = models.CharField(
        max_length=64,
        blank=True,
        null=True,
        help_text="Structured rationale category for override (required if overridden)"
    )
    override_note = models.TextField(
        max_length=500,
        blank=True,
        null=True,
        help_text="Optional brief contextual rationale (max 500 chars; required if reason is Other)"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp of review submission"
    )

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"HumanReview {str(self.id)[:8]}... by {self.reviewer_code} ({self.review_action})"

    @property
    def action_display(self) -> str:
        if self.review_action == 'accepted':
            return "Recommendation Accepted"
        elif self.review_action == 'overridden':
            return "Recommendation Overridden"
        return self.review_action

    @property
    def final_decision_text(self) -> str:
        if self.final_referral_recommended:
            return "Refer for Stage-2 HbA1c assessment"
        return "No referral recommended at current operating point"

    @property
    def override_reason_display(self) -> str:
        if not self.override_reason_code:
            return ""
        return ALL_OVERRIDE_REASONS_DICT.get(self.override_reason_code, self.override_reason_code)

    def clean(self):
        super().clean()
        if not hasattr(self, 'screening_record') or not self.screening_record:
            return

        ai_rec = self.screening_record.ai_referral_recommended

        if self.review_action == 'accepted':
            if self.final_referral_recommended != ai_rec:
                raise ValidationError("Accepted review must have final decision matching AI recommendation.")
            if self.override_reason_code and self.override_reason_code != 'no_learning_signal':
                raise ValidationError("Accepted review must not specify an override reason.")

        elif self.review_action == 'overridden':
            if self.final_referral_recommended == ai_rec:
                raise ValidationError("Overridden review must have final decision different from AI recommendation.")
            if not self.override_reason_code:
                raise ValidationError("Overridden review requires a structured override reason code.")

            learning_codes = [c[0] for c in OVERRIDE_LEARNING_FACTORS]
            if ai_rec:
                valid_codes = [c[0] for c in OVERRIDE_REASONS_REFER_TO_NO_REFER] + learning_codes
            else:
                valid_codes = [c[0] for c in OVERRIDE_REASONS_NO_REFER_TO_REFER] + learning_codes

            if self.override_reason_code not in valid_codes:
                raise ValidationError(f"Invalid reason code '{self.override_reason_code}' for override.")

            if self.override_reason_code == 'other':
                if not self.override_note or not self.override_note.strip():
                    raise ValidationError("Provide a short reason when selecting Other.")


# Structured Override Rationale Taxonomies
OVERRIDE_REASONS_REFER_TO_NO_REFER = [
    ('additional_context_reduces_concern', 'Additional context supports not referring at this time'),
    ('input_quality_concern', 'Concern about the quality or accuracy of one or more screening inputs'),
    ('repeat_assessment_preferred', 'Repeat or additional assessment is preferred before referral'),
    ('other', 'Other reason'),
]

OVERRIDE_REASONS_NO_REFER_TO_REFER = [
    ('additional_context_increases_concern', 'Additional context supports referral'),
    ('input_quality_concern', 'Concern about the quality or accuracy of one or more screening inputs'),
    ('precautionary_referral', 'Referral is preferred as a precaution'),
    ('other', 'Other reason'),
]

OVERRIDE_LEARNING_FACTORS = [
    ('bmi_overweighted', 'BMI was over-weighted'),
    ('age_overweighted', 'Age was over-weighted'),
    ('waist_overweighted', 'Waist circumference was over-weighted'),
    ('hypertension_overweighted', 'Hypertension was over-weighted'),
    ('smoking_overweighted', 'Smoking history was over-weighted'),
    ('sedentary_overweighted', 'Sedentary time was over-weighted'),
    ('multiple_factors_overweighted', 'Multiple factors were over-weighted'),
    ('other', 'Other'),
    ('no_learning_signal', 'No learning signal'),
]

ALL_OVERRIDE_REASONS_DICT = {
    **dict(OVERRIDE_REASONS_REFER_TO_NO_REFER),
    **dict(OVERRIDE_REASONS_NO_REFER_TO_REFER),
    **dict(OVERRIDE_LEARNING_FACTORS),
}


class Stage2Assessment(models.Model):
    """
    Stage-2 Confirmatory Laboratory Assessment Domain Entity (Phase D2.8).

    Records an entered laboratory HbA1c measurement and categorizes it
    into an authoritative laboratory range based on a frozen clinical reference.

    RESEARCH & EPISTEMIC GOVERNANCE RULES:
    1. Stage 2 is NOT a machine learning model; 0 GAM or XAI calls are executed.
    2. Does NOT produce an automated diagnosis or claim disease truth.
    3. Categorizes solely into standard laboratory range categories (Normal, Prediabetes, Diabetes range).
    4. Only accessible when HumanReview.final_referral_recommended is True.
    5. Directly linked via OneToOneField to HumanReview (the referral decision authority).
    6. Range and reference version are strictly server-derived and immutable once created.
    """
    RANGE_CHOICES = [
        ('normal_range', 'Normal-range'),
        ('prediabetes_range', 'Prediabetes-range'),
        ('diabetes_range', 'Diabetes-range'),
    ]

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique anonymous Stage-2 assessment identifier (UUIDv4)"
    )
    human_review = models.OneToOneField(
        'HumanReview',
        on_delete=models.PROTECT,
        related_name='stage2_assessment',
        help_text="Parent finalized HumanReview that authorized this Stage-2 assessment"
    )
    hba1c_percent = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        help_text="Entered HbA1c percentage (e.g. 5.70, 6.50)"
    )
    laboratory_range = models.CharField(
        max_length=32,
        choices=RANGE_CHOICES,
        help_text="Server-derived laboratory range category"
    )
    range_rule_version = models.CharField(
        max_length=64,
        default="ADA_2026_A1C_RANGE_V1",
        help_text="Frozen reference rule version identifier"
    )
    entry_method = models.CharField(
        max_length=20,
        default='manual',
        help_text="Provenance entry method (e.g. manual)"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp of Stage-2 assessment confirmation"
    )

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return (
            f"Stage2Assessment {str(self.id)[:8]}...: "
            f"{self.hba1c_percent}% ({self.get_laboratory_range_display()}) "
            f"[{self.range_rule_version}]"
        )

    @property
    def range_display(self) -> str:
        return self.get_laboratory_range_display()

    @property
    def interpretation_copy(self) -> str:
        if self.laboratory_range == 'normal_range':
            return "Entered HbA1c falls below the 5.7% prediabetes-range threshold."
        elif self.laboratory_range == 'prediabetes_range':
            return "Entered HbA1c falls within the 5.7% to <6.5% laboratory range."
        elif self.laboratory_range == 'diabetes_range':
            return (
                "Entered HbA1c falls within the ≥6.5% laboratory range used in diabetes diagnostic criteria. "
                "This prototype does not establish a diagnosis; clinical diagnosis may require confirmatory "
                "testing and additional clinical context."
            )
        return ""

    @property
    def diagnostic_caveat(self) -> str:
        return (
            "This range presentation is not an automated diagnosis. "
            "In the absence of unequivocal hyperglycemia, clinical diagnosis generally "
            "requires appropriate confirmatory testing. This prototype does not evaluate "
            "whether confirmation has occurred."
        )

    @property
    def assay_limitation_note(self) -> str:
        return (
            "HbA1c interpretation can depend on laboratory method and clinical context. "
            "This research prototype categorizes the entered numeric value only."
        )

    def clean(self):
        super().clean()
        if not hasattr(self, 'human_review') or not self.human_review:
            raise ValidationError("Stage2Assessment must be linked to a finalized HumanReview.")

        if not self.human_review.final_referral_recommended:
            raise ValidationError(
                "Stage2Assessment cannot be created for a screening review where final referral was not recommended."
            )

        # Re-derive range server-side to enforce anti-tampering
        from .services.hba1c_range import classify_hba1c_range, RANGE_RULE_VERSION
        try:
            derived = classify_hba1c_range(self.hba1c_percent)
        except Exception as e:
            raise ValidationError(f"Invalid HbA1c percentage: {e}")

        if self.laboratory_range != derived.range_code:
            raise ValidationError(
                f"Laboratory range mismatch: expected '{derived.range_code}', got '{self.laboratory_range}'."
            )

        if self.range_rule_version != derived.rule_version:
            raise ValidationError(
                f"Rule version mismatch: expected '{derived.rule_version}', got '{self.range_rule_version}'."
            )


# ===========================================================================
# HUMAN FEEDBACK LEARNING LOOP MODELS
# Appended for the feedback-driven adaptation experiment.
# All existing models above remain IMMUTABLE.
# ===========================================================================


class ModelVersion(models.Model):
    """
    Versioned model registry for the feedback learning loop.

    Tracks the lifecycle of model versions:
      baseline → candidate → validation → active → (rolled_back)

    GOVERNANCE:
    - Exactly ONE version may have is_active=True at any time.
    - The baseline (GAM-v1) is always recoverable.
    - Historical predictions reference the version used; they are NEVER recalculated.
    - The frozen GAM artifact itself is NEVER modified; only the adaptation layer changes.
    """
    VERSION_TYPE_CHOICES = [
        ('baseline', 'Baseline (Frozen GAM)'),
        ('candidate', 'Candidate (Pending Validation)'),
        ('active', 'Active (Validated & Deployed)'),
        ('rejected', 'Rejected (Failed Validation)'),
        ('rolled_back', 'Rolled Back'),
    ]

    VALIDATION_STATUS_CHOICES = [
        ('not_applicable', 'Not Applicable (Baseline)'),
        ('pending', 'Pending Validation'),
        ('passed', 'Passed Validation'),
        ('failed', 'Failed Validation'),
    ]

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique model version identifier"
    )
    version_label = models.CharField(
        max_length=100,
        unique=True,
        help_text="Human-readable version label (e.g., 'GAM-v1', 'GAM-v2-candidate')"
    )
    version_type = models.CharField(
        max_length=20,
        choices=VERSION_TYPE_CHOICES,
        help_text="Current lifecycle state of this version"
    )
    parent_version = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='derived_versions',
        help_text="Parent version this was derived from (lineage tracking)"
    )
    description = models.TextField(
        blank=True,
        default="",
        help_text="Description of what this version contains or changed"
    )
    # Artifact provenance
    base_model_sha256 = models.CharField(
        max_length=64,
        default="204a94ff072ef4f1edecebf5a643738c006bbf010f3817b4bb798d3ea6fef41d",
        help_text="SHA-256 of the frozen GAM model artifact (always the same)"
    )
    adaptation_artifact_path = models.CharField(
        max_length=500,
        blank=True,
        default="",
        help_text="Path to the serialized adaptation layer artifact (empty for baseline)"
    )
    adaptation_sha256 = models.CharField(
        max_length=64,
        blank=True,
        default="",
        help_text="SHA-256 of the adaptation layer artifact (empty for baseline)"
    )
    # Training provenance
    feedback_count_used = models.IntegerField(
        default=0,
        help_text="Number of eligible feedback records used to train the adaptation layer"
    )
    training_data_description = models.TextField(
        blank=True,
        default="",
        help_text="Description of training data used (excluding final-test N=812)"
    )
    # Validation
    validation_status = models.CharField(
        max_length=20,
        choices=VALIDATION_STATUS_CHOICES,
        default='not_applicable',
        help_text="Validation status of this version"
    )
    validation_metrics = models.JSONField(
        null=True,
        blank=True,
        help_text="Validation metrics JSON (feedback-loop experiment metrics, NOT final-test)"
    )
    # Lifecycle timestamps
    is_active = models.BooleanField(
        default=False,
        help_text="Whether this is the currently active version (exactly 1 active at a time)"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp of version creation"
    )
    activated_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp when this version was activated"
    )
    deactivated_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp when this version was deactivated"
    )
    notes = models.TextField(
        blank=True,
        default="",
        help_text="Administrative notes"
    )

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['is_active']),
            models.Index(fields=['version_type']),
        ]

    @property
    def is_baseline(self) -> bool:
        return self.version_type == 'baseline'

    def __str__(self):
        active_tag = " [ACTIVE]" if self.is_active else ""
        return f"ModelVersion {self.version_label} ({self.version_type}){active_tag}"


class HumanFeedback(models.Model):
    """
    Structured feedback record linked to a finalized HumanReview.

    Captures:
    1. The human-selected structured feedback category (CANONICAL learning signal).
    2. Optional raw free-text feedback (preserved for auditability).
    3. NLP interpretation of free-text (preserved alongside raw text).
    4. Learning eligibility and status.
    5. Model version at time of feedback.
    6. Taxonomy version used.

    GOVERNANCE:
    - Human feedback is NOT automatically biological ground truth.
    - The structured category is the canonical signal, NOT raw NLP output.
    - This record does NOT overwrite the ScreeningRecord's AI prediction.
    - Raw text and NLP output are both preserved; neither is discarded.
    """
    LEARNING_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('included', 'Included in Learning Batch'),
        ('excluded', 'Excluded from Learning'),
        ('expired', 'Expired'),
    ]

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique feedback record identifier"
    )
    human_review = models.OneToOneField(
        'HumanReview',
        on_delete=models.PROTECT,
        related_name='feedback',
        help_text="Parent HumanReview this feedback is associated with"
    )
    # Structured feedback (CANONICAL learning signal)
    structured_category = models.CharField(
        max_length=64,
        help_text="Master taxonomy category_id (canonical learning signal)"
    )
    relevant_feature = models.CharField(
        max_length=64,
        blank=True,
        null=True,
        help_text="Primary relevant Stage-1 predictor (e.g., 'bmi', 'age'), if applicable"
    )
    feedback_direction = models.CharField(
        max_length=30,
        help_text="Learning direction: reduce_influence, increase_influence, contextual_adjustment, reduce_global, increase_global, no_learning"
    )
    # Optional free-text (preserved for audit)
    feedback_text = models.TextField(
        blank=True,
        default="",
        help_text="Optional raw human free-text feedback (preserved verbatim for auditability)"
    )
    # NLP interpretation (preserved alongside raw text)
    nlp_confidence = models.FloatField(
        null=True,
        blank=True,
        help_text="NLP classification confidence [0, 1] (null if no free-text provided)"
    )
    nlp_raw_output = models.JSONField(
        null=True,
        blank=True,
        help_text="Complete NLP interpretation output (preserved for auditability)"
    )
    # Learning eligibility
    is_eligible_for_learning = models.BooleanField(
        default=False,
        help_text="Whether this feedback is eligible to be included in a learning batch"
    )
    learning_status = models.CharField(
        max_length=20,
        choices=LEARNING_STATUS_CHOICES,
        default='pending',
        help_text="Current learning pipeline status"
    )
    # Provenance
    model_version_at_feedback = models.CharField(
        max_length=100,
        default="GAM-v1",
        help_text="Version label of the active model when feedback was submitted"
    )
    taxonomy_version = models.CharField(
        max_length=20,
        help_text="Taxonomy version used for this feedback record"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp of feedback submission"
    )

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['is_eligible_for_learning']),
            models.Index(fields=['learning_status']),
            models.Index(fields=['structured_category']),
        ]

    def __str__(self):
        return (
            f"HumanFeedback {str(self.id)[:8]}... "
            f"cat={self.structured_category} "
            f"eligible={self.is_eligible_for_learning}"
        )


class FeedbackLearningBatch(models.Model):
    """
    Tracks a batch learning update using accumulated eligible feedback.

    Lifecycle:
      pending → training → validating → activated | rejected | failed

    GOVERNANCE:
    - Minimum feedback count is enforced before training.
    - Validation MUST pass before activation (never uses final-test N=812).
    - Failed batches are preserved for audit, not deleted.
    - Each batch records exactly which feedback records were used.
    """
    BATCH_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('training', 'Training'),
        ('validating', 'Validating'),
        ('activated', 'Activated'),
        ('rejected', 'Rejected'),
        ('failed', 'Failed'),
    ]

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique batch identifier"
    )
    batch_label = models.CharField(
        max_length=100,
        help_text="Human-readable batch label (e.g., 'batch-001')"
    )
    source_version = models.ForeignKey(
        'ModelVersion',
        on_delete=models.PROTECT,
        related_name='learning_batches_as_source',
        help_text="Model version that was active when this batch was created"
    )
    candidate_version = models.ForeignKey(
        'ModelVersion',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='learning_batches_as_candidate',
        help_text="Candidate ModelVersion produced by this batch (null if training not yet done)"
    )
    feedback_records = models.ManyToManyField(
        'HumanFeedback',
        blank=True,
        related_name='learning_batches',
        help_text="Feedback records included in this learning batch"
    )
    feedback_count = models.IntegerField(
        default=0,
        help_text="Number of eligible feedback records in this batch"
    )
    status = models.CharField(
        max_length=20,
        choices=BATCH_STATUS_CHOICES,
        default='pending',
        help_text="Current batch lifecycle status"
    )
    validation_metrics = models.JSONField(
        null=True,
        blank=True,
        help_text="Validation metrics for the candidate version (feedback-experiment metrics only)"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp of batch creation"
    )
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp of batch completion (activation, rejection, or failure)"
    )
    error_log = models.TextField(
        blank=True,
        default="",
        help_text="Error details if batch failed"
    )

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"FeedbackLearningBatch {self.batch_label} ({self.status})"


class SimilarCaseComparison(models.Model):
    """
    Records a controlled before/after experiment comparing AI behavior
    on a subsequent similar case (Case B) against baseline and adapted model.

    This is the CORE experiment record answering:
    'Can human feedback influence AI behavior on a subsequent similar case?'

    GOVERNANCE:
    - Case A (source_case) prediction is NEVER modified.
    - Case B (target_case) is a SEPARATE observation.
    - Both baseline and adapted outputs are recorded.
    - A changed, unchanged, or partially changed result are all valid outcomes.
    - This record does NOT claim causality beyond the controlled experiment.
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique comparison identifier"
    )
    source_case = models.ForeignKey(
        'ScreeningRecord',
        on_delete=models.PROTECT,
        related_name='feedback_source_comparisons',
        help_text="Case A: the screening record that generated the feedback"
    )
    target_case = models.ForeignKey(
        'ScreeningRecord',
        on_delete=models.PROTECT,
        related_name='feedback_target_comparisons',
        help_text="Case B: the subsequent similar case being compared"
    )
    # Similarity metadata
    similarity_score = models.FloatField(
        help_text="Computed similarity score [0, 1]"
    )
    similarity_method = models.CharField(
        max_length=50,
        default="normalized_euclidean_7feat",
        help_text="Similarity method identifier"
    )
    similarity_features_used = models.JSONField(
        help_text="List of features used for similarity computation"
    )
    similarity_normalization_version = models.CharField(
        max_length=20,
        default="1.0",
        help_text="Normalization bounds version used"
    )
    # Baseline (frozen GAM v1) outputs for Case B
    baseline_version = models.ForeignKey(
        'ModelVersion',
        on_delete=models.PROTECT,
        related_name='baseline_comparisons',
        help_text="Baseline model version used"
    )
    baseline_probability = models.FloatField(
        help_text="Case B probability from baseline model"
    )
    baseline_recommendation = models.BooleanField(
        help_text="Case B referral recommendation from baseline model"
    )
    # Updated (adapted) model outputs for Case B
    updated_version = models.ForeignKey(
        'ModelVersion',
        on_delete=models.PROTECT,
        related_name='updated_comparisons',
        help_text="Updated/adapted model version used"
    )
    updated_probability = models.FloatField(
        help_text="Case B probability from adapted model"
    )
    updated_recommendation = models.BooleanField(
        help_text="Case B referral recommendation from adapted model"
    )
    # Comparison results
    probability_delta = models.FloatField(
        help_text="Difference: updated_probability - baseline_probability"
    )
    recommendation_changed = models.BooleanField(
        help_text="Whether the referral recommendation changed between versions"
    )
    # Feedback provenance
    feedback_category = models.CharField(
        max_length=64,
        help_text="Primary feedback category that influenced this comparison"
    )
    learning_batch = models.ForeignKey(
        'FeedbackLearningBatch',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='comparisons',
        help_text="Learning batch that produced the updated version"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp of comparison creation"
    )

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        changed = "CHANGED" if self.recommendation_changed else "UNCHANGED"
        return (
            f"Comparison {str(self.id)[:8]}... "
            f"Δp={self.probability_delta:+.4f} ({changed})"
        )


# ==============================================================================
# EVALUATION STUDY & DASHBOARD QUESTIONNAIRE MODELS (Protocol E1 v1.0.3)
# ==============================================================================

class EvaluationRespondent(models.Model):
    """
    Anonymous participant identifier for user evaluation study (Protocol E1 v1.0.3).
    Privacy-preserving: No names, emails, student IDs, or direct personal identifiers stored.
    """
    AGE_CHOICES = [
        ('18-24', '18 – 24 tahun'),
        ('25-34', '25 – 34 tahun'),
        ('35-49', '35 – 49 tahun'),
        ('50+', '50 tahun ke atas'),
    ]
    EDUCATION_CHOICES = [
        ('high_school', 'SMA / SMK / Sederajat'),
        ('undergrad', 'Sarjana Terapan / Mahasiswa S1'),
        ('bachelor', 'Lulusan Sarjana (S1 / D4)'),
        ('postgrad', 'Magister (S2) / Spesialis / Doktoral (S3)'),
    ]
    TECHNICAL_EXP_CHOICES = [
        ('none', 'Tidak pernah / Belum pernah'),
        ('occasional', 'Kadang-kadang (1–2 kali per bulan)'),
        ('frequent', 'Sering / Rutin (mingguan atau harian)'),
    ]
    HEALTH_BG_CHOICES = [
        ('none', 'Tidak memiliki latar belakang bidang kesehatan'),
        ('student', 'Mahasiswa rumpun ilmu kesehatan (Kedokteran, Keperawatan, Gizi, Farmasi, Kesmas)'),
        ('practitioner', 'Tenaga kesehatan / Dokter / Praktisi klinis aktif'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    respondent_code = models.CharField(
        max_length=50,
        unique=True,
        help_text="Anonymous participant tracking code (e.g. RESP-xxxx)"
    )
    age_group = models.CharField(max_length=20, choices=AGE_CHOICES)
    education_level = models.CharField(max_length=20, choices=EDUCATION_CHOICES)
    technical_background = models.CharField(max_length=20, choices=TECHNICAL_EXP_CHOICES)
    health_background = models.CharField(max_length=20, choices=HEALTH_BG_CHOICES)
    consent_given = models.BooleanField(default=True)
    consent_timestamp = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Respondent {self.respondent_code} ({self.age_group})"


class EvaluationSession(models.Model):
    """
    Tracks an individual evaluation session for an anonymous respondent.
    Enforces that the evaluation environment remains frozen on GAM-v1.
    """
    STATUS_CHOICES = [
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('abandoned', 'Abandoned'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    respondent = models.ForeignKey(
        EvaluationRespondent,
        on_delete=models.CASCADE,
        related_name='sessions'
    )
    session_token = models.CharField(max_length=64, unique=True, default=uuid.uuid4)
    app_version = models.CharField(max_length=50, default='research-prototype-v1.0')
    model_version = models.CharField(max_length=50, default='GAM-v1')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in_progress')
    practice_completed = models.BooleanField(default=False)
    questionnaire_completed = models.BooleanField(default=False)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-started_at']

    def __str__(self):
        return f"Session {str(self.id)[:8]} ({self.status}) - {self.respondent.respondent_code}"


class EvaluationEvent(models.Model):
    """
    Audit log of research-relevant milestone events during an evaluation session.
    Logs research-significant workflow milestones, not raw pointer/UI clicks.
    """
    EVENT_CHOICES = [
        ('session_started', 'Session Started'),
        ('practice_started', 'Practice Started'),
        ('practice_completed', 'Practice Completed'),
        ('stage1_completed', 'Stage 1 Completed'),
        ('xai_viewed', 'XAI Explanation Viewed'),
        ('human_review_completed', 'Human Review Completed'),
        ('override_recorded', 'Override Recorded'),
        ('stage2_completed', 'Stage 2 Completed'),
        ('feedback_submitted', 'Feedback Submitted'),
        ('questionnaire_started', 'Questionnaire Started'),
        ('questionnaire_submitted', 'Questionnaire Submitted'),
        ('session_completed', 'Session Completed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(
        EvaluationSession,
        on_delete=models.CASCADE,
        related_name='events'
    )
    event_name = models.CharField(max_length=50, choices=EVENT_CHOICES)
    event_data = models.JSONField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"[{self.timestamp.strftime('%H:%M:%S')}] {self.event_name} ({self.session.respondent.respondent_code})"


class QuestionnaireResponse(models.Model):
    """
    Stores comprehensive post-task questionnaire responses from participants.
    Completely decoupled from model feedback and learning loop.
    Contains:
    - Section A: Objective Comprehension (8 items C1-C8, server-scored 0-8, %)
    - Section B: System Usability Scale (10 items, Sharfina & Santoso 2016, scored 0-100)
    - Section C: Dashboard Clarity (5 items DQ1-DQ5, discrete 1-5)
    - Section D: Qualitative Feedback (3 open-ended text questions OQ1-OQ3)
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.OneToOneField(
        EvaluationSession,
        on_delete=models.CASCADE,
        related_name='questionnaire_response'
    )
    respondent = models.ForeignKey(
        EvaluationRespondent,
        on_delete=models.CASCADE,
        related_name='questionnaire_responses'
    )
    app_version = models.CharField(max_length=50, default='research-prototype-v1.0')
    model_version = models.CharField(max_length=50, default='GAM-v1')

    # Section A: 8 Objective Comprehension Items (Raw participant answers: 'A', 'B', 'C', 'D')
    c1_answer = models.CharField(max_length=5)
    c2_answer = models.CharField(max_length=5)
    c3_answer = models.CharField(max_length=5)
    c4_answer = models.CharField(max_length=5)
    c5_answer = models.CharField(max_length=5)
    c6_answer = models.CharField(max_length=5)
    c7_answer = models.CharField(max_length=5)
    c8_answer = models.CharField(max_length=5)

    # Scored on server side (Never revealed to participant during test)
    comprehension_score = models.PositiveSmallIntegerField(
        help_text="Count of correct comprehension answers (0 to 8)"
    )
    comprehension_pct = models.FloatField(
        help_text="Comprehension percentage: (score / 8) * 100"
    )

    # Section B: 10 Indonesian SUS Items (Likert 1 to 5)
    sus_1 = models.PositiveSmallIntegerField()
    sus_2 = models.PositiveSmallIntegerField()
    sus_3 = models.PositiveSmallIntegerField()
    sus_4 = models.PositiveSmallIntegerField()
    sus_5 = models.PositiveSmallIntegerField()
    sus_6 = models.PositiveSmallIntegerField()
    sus_7 = models.PositiveSmallIntegerField()
    sus_8 = models.PositiveSmallIntegerField()
    sus_9 = models.PositiveSmallIntegerField()
    sus_10 = models.PositiveSmallIntegerField()

    # Scored standard Brooke / Sharfina & Santoso formula: odd-1, 5-even, sum * 2.5
    sus_score = models.FloatField(
        help_text="Standardized System Usability Scale score (0.0 to 100.0)"
    )

    # Section C: 5 Dashboard Clarity Items (Likert 1 to 5, analyzed individually)
    clarity_1 = models.PositiveSmallIntegerField()
    clarity_2 = models.PositiveSmallIntegerField()
    clarity_3 = models.PositiveSmallIntegerField()
    clarity_4 = models.PositiveSmallIntegerField()
    clarity_5 = models.PositiveSmallIntegerField()

    # Section D: 3 Open-Ended Qualitative Feedback Items
    open_1 = models.TextField(blank=True, default="", help_text="OQ1: Bagian paling membantu")
    open_2 = models.TextField(blank=True, default="", help_text="OQ2: Bagian paling membingungkan")
    open_3 = models.TextField(blank=True, default="", help_text="OQ3: Saran perbaikan utama")

    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-submitted_at']

    def __str__(self):
        return (
            f"Questionnaire for {self.respondent.respondent_code}: "
            f"SUS={self.sus_score:.1f}, Comp={self.comprehension_score}/8 ({self.comprehension_pct:.1f}%)"
        )
