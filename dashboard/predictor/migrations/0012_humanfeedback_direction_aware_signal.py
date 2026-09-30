"""
Migration: Add direction-aware structured signal fields to HumanFeedback.

Taxonomy v2.0 adds explicit target_feature, direction, and scope fields.

All new fields are nullable to preserve backward compatibility with
existing v1.0 HumanFeedback records — historical raw values remain unchanged.
"""

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('predictor', '0011_evaluation_linkage_and_governance'),
    ]

    operations = [
        # Add target_feature field
        migrations.AddField(
            model_name='humanfeedback',
            name='target_feature',
            field=models.CharField(
                blank=True,
                help_text='Canonical target feature: bmi, age, waist, hypertension, smoking, sedentary, multiple, other, none',
                max_length=32,
                null=True,
            ),
        ),
        # Add direction field
        migrations.AddField(
            model_name='humanfeedback',
            name='direction',
            field=models.CharField(
                blank=True,
                help_text='Canonical direction: reduce, increase, adjust, contextual, none',
                max_length=20,
                null=True,
            ),
        ),
        # Add scope field
        migrations.AddField(
            model_name='humanfeedback',
            name='scope',
            field=models.CharField(
                blank=True,
                help_text='Canonical scope: feature_specific, multiple_features, contextual, none',
                max_length=32,
                null=True,
            ),
        ),
    ]
