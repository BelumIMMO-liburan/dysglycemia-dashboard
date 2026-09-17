from django.contrib import admin
from .models import Prediction, Override


@admin.register(Prediction)
class PredictionAdmin(admin.ModelAdmin):
    list_display = ['id', 'timestamp', 'model_used', 'prediction', 'confidence', 'threshold', 'is_reviewed']
    list_filter = ['model_used', 'prediction', 'is_reviewed']
    search_fields = ['model_used']
    readonly_fields = ['timestamp', 'patient_data', 'model_used', 'prediction', 'confidence', 'threshold', 'shap_values']


@admin.register(Override)
class OverrideAdmin(admin.ModelAdmin):
    list_display = ['id', 'timestamp', 'prediction', 'doctor_name', 'decision', 'override_value']
    list_filter = ['decision', 'doctor_name']
    search_fields = ['doctor_name', 'reason']
    readonly_fields = ['timestamp']
