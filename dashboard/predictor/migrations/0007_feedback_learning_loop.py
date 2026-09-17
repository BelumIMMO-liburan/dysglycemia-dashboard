"""
Django migration for Human Feedback Learning Loop models.

Adds:
- ModelVersion: Versioned model registry
- HumanFeedback: Structured feedback linked to HumanReview
- FeedbackLearningBatch: Batch learning update tracking
- SimilarCaseComparison: Before/after experiment records

All existing tables remain UNTOUCHED.
"""

import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('predictor', '0006_stage2assessment'),
    ]

    operations = [
        migrations.CreateModel(
            name='ModelVersion',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, help_text='Unique model version identifier')),
                ('version_label', models.CharField(help_text="Human-readable version label (e.g., 'GAM-v1', 'GAM-v2-candidate')", max_length=100, unique=True)),
                ('version_type', models.CharField(choices=[('baseline', 'Baseline (Frozen GAM)'), ('candidate', 'Candidate (Pending Validation)'), ('active', 'Active (Validated & Deployed)'), ('rejected', 'Rejected (Failed Validation)'), ('rolled_back', 'Rolled Back')], help_text='Current lifecycle state of this version', max_length=20)),
                ('parent_version', models.ForeignKey(blank=True, help_text='Parent version this was derived from (lineage tracking)', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='derived_versions', to='predictor.modelversion')),
                ('description', models.TextField(blank=True, default='', help_text='Description of what this version contains or changed')),
                ('base_model_sha256', models.CharField(default='204a94ff072ef4f1edecebf5a643738c006bbf010f3817b4bb798d3ea6fef41d', help_text='SHA-256 of the frozen GAM model artifact (always the same)', max_length=64)),
                ('adaptation_artifact_path', models.CharField(blank=True, default='', help_text='Path to the serialized adaptation layer artifact (empty for baseline)', max_length=500)),
                ('adaptation_sha256', models.CharField(blank=True, default='', help_text='SHA-256 of the adaptation layer artifact (empty for baseline)', max_length=64)),
                ('feedback_count_used', models.IntegerField(default=0, help_text='Number of eligible feedback records used to train the adaptation layer')),
                ('training_data_description', models.TextField(blank=True, default='', help_text='Description of training data used (excluding final-test N=812)')),
                ('validation_status', models.CharField(choices=[('not_applicable', 'Not Applicable (Baseline)'), ('pending', 'Pending Validation'), ('passed', 'Passed Validation'), ('failed', 'Failed Validation')], default='not_applicable', help_text='Validation status of this version', max_length=20)),
                ('validation_metrics', models.JSONField(blank=True, help_text='Validation metrics JSON (feedback-loop experiment metrics, NOT final-test)', null=True)),
                ('is_active', models.BooleanField(default=False, help_text='Whether this is the currently active version (exactly 1 active at a time)')),
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='Timestamp of version creation')),
                ('activated_at', models.DateTimeField(blank=True, help_text='Timestamp when this version was activated', null=True)),
                ('deactivated_at', models.DateTimeField(blank=True, help_text='Timestamp when this version was deactivated', null=True)),
                ('notes', models.TextField(blank=True, default='', help_text='Administrative notes')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='modelversion',
            index=models.Index(fields=['is_active'], name='predictor_m_is_acti_idx'),
        ),
        migrations.AddIndex(
            model_name='modelversion',
            index=models.Index(fields=['version_type'], name='predictor_m_version_idx'),
        ),
        migrations.CreateModel(
            name='HumanFeedback',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, help_text='Unique feedback record identifier')),
                ('human_review', models.OneToOneField(help_text='Parent HumanReview this feedback is associated with', on_delete=django.db.models.deletion.PROTECT, related_name='feedback', to='predictor.humanreview')),
                ('structured_category', models.CharField(help_text='Master taxonomy category_id (canonical learning signal)', max_length=64)),
                ('relevant_feature', models.CharField(blank=True, help_text="Primary relevant Stage-1 predictor (e.g., 'bmi', 'age'), if applicable", max_length=64, null=True)),
                ('feedback_direction', models.CharField(help_text='Learning direction', max_length=30)),
                ('feedback_text', models.TextField(blank=True, default='', help_text='Optional raw human free-text feedback (preserved verbatim for auditability)')),
                ('nlp_confidence', models.FloatField(blank=True, help_text='NLP classification confidence [0, 1]', null=True)),
                ('nlp_raw_output', models.JSONField(blank=True, help_text='Complete NLP interpretation output (preserved for auditability)', null=True)),
                ('is_eligible_for_learning', models.BooleanField(default=False, help_text='Whether this feedback is eligible to be included in a learning batch')),
                ('learning_status', models.CharField(choices=[('pending', 'Pending'), ('included', 'Included in Learning Batch'), ('excluded', 'Excluded from Learning'), ('expired', 'Expired')], default='pending', help_text='Current learning pipeline status', max_length=20)),
                ('model_version_at_feedback', models.CharField(default='GAM-v1', help_text='Version label of the active model when feedback was submitted', max_length=100)),
                ('taxonomy_version', models.CharField(help_text='Taxonomy version used for this feedback record', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='Timestamp of feedback submission')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='humanfeedback',
            index=models.Index(fields=['is_eligible_for_learning'], name='predictor_hf_eligible_idx'),
        ),
        migrations.AddIndex(
            model_name='humanfeedback',
            index=models.Index(fields=['learning_status'], name='predictor_hf_status_idx'),
        ),
        migrations.AddIndex(
            model_name='humanfeedback',
            index=models.Index(fields=['structured_category'], name='predictor_hf_category_idx'),
        ),
        migrations.CreateModel(
            name='FeedbackLearningBatch',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, help_text='Unique batch identifier')),
                ('batch_label', models.CharField(help_text="Human-readable batch label (e.g., 'batch-001')", max_length=100)),
                ('source_version', models.ForeignKey(help_text='Model version that was active when this batch was created', on_delete=django.db.models.deletion.PROTECT, related_name='learning_batches_as_source', to='predictor.modelversion')),
                ('candidate_version', models.ForeignKey(blank=True, help_text='Candidate ModelVersion produced by this batch', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='learning_batches_as_candidate', to='predictor.modelversion')),
                ('feedback_records', models.ManyToManyField(blank=True, help_text='Feedback records included in this learning batch', related_name='learning_batches', to='predictor.humanfeedback')),
                ('feedback_count', models.IntegerField(default=0, help_text='Number of eligible feedback records in this batch')),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('training', 'Training'), ('validating', 'Validating'), ('activated', 'Activated'), ('rejected', 'Rejected'), ('failed', 'Failed')], default='pending', help_text='Current batch lifecycle status', max_length=20)),
                ('validation_metrics', models.JSONField(blank=True, help_text='Validation metrics for the candidate version', null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='Timestamp of batch creation')),
                ('completed_at', models.DateTimeField(blank=True, help_text='Timestamp of batch completion', null=True)),
                ('error_log', models.TextField(blank=True, default='', help_text='Error details if batch failed')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='SimilarCaseComparison',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, help_text='Unique comparison identifier')),
                ('source_case', models.ForeignKey(help_text='Case A: the screening record that generated the feedback', on_delete=django.db.models.deletion.PROTECT, related_name='feedback_source_comparisons', to='predictor.screeningrecord')),
                ('target_case', models.ForeignKey(help_text='Case B: the subsequent similar case being compared', on_delete=django.db.models.deletion.PROTECT, related_name='feedback_target_comparisons', to='predictor.screeningrecord')),
                ('similarity_score', models.FloatField(help_text='Computed similarity score [0, 1]')),
                ('similarity_method', models.CharField(default='normalized_euclidean_7feat', help_text='Similarity method identifier', max_length=50)),
                ('similarity_features_used', models.JSONField(help_text='List of features used for similarity computation')),
                ('similarity_normalization_version', models.CharField(default='1.0', help_text='Normalization bounds version used', max_length=20)),
                ('baseline_version', models.ForeignKey(help_text='Baseline model version used', on_delete=django.db.models.deletion.PROTECT, related_name='baseline_comparisons', to='predictor.modelversion')),
                ('baseline_probability', models.FloatField(help_text='Case B probability from baseline model')),
                ('baseline_recommendation', models.BooleanField(help_text='Case B referral recommendation from baseline model')),
                ('updated_version', models.ForeignKey(help_text='Updated/adapted model version used', on_delete=django.db.models.deletion.PROTECT, related_name='updated_comparisons', to='predictor.modelversion')),
                ('updated_probability', models.FloatField(help_text='Case B probability from adapted model')),
                ('updated_recommendation', models.BooleanField(help_text='Case B referral recommendation from adapted model')),
                ('probability_delta', models.FloatField(help_text='Difference: updated_probability - baseline_probability')),
                ('recommendation_changed', models.BooleanField(help_text='Whether the referral recommendation changed between versions')),
                ('feedback_category', models.CharField(help_text='Primary feedback category that influenced this comparison', max_length=64)),
                ('learning_batch', models.ForeignKey(blank=True, help_text='Learning batch that produced the updated version', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='comparisons', to='predictor.feedbacklearningbatch')),
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='Timestamp of comparison creation')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
