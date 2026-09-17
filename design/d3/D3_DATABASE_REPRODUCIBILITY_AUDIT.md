# D3 Database Schema & Migration Reproducibility Audit

**Audit Date:** 2026-09-05  
**Database Engine:** SQLite 3.x (Local Research Prototype)  
**Schema Status:** 100% REPRODUCIBLE FROM MIGRATIONS FROM ZERO

---

## 1. Domain Entities Schema Architecture

The formal relational schema comprises four primary entities spanning the two-stage screening workflow:

```
┌─────────────────────────────────────────────────────────┐
│                     ScreeningRecord                     │
│  id: UUID (PK)                                          │
│  created_at: DateTime                                   │
│  age: Integer (18-85)                                   │
│  sex: CharField ('male'/'female')                       │
│  bmi: DecimalField (10.0-70.0)                          │
│  waist_cm: DecimalField (40.0-200.0)                    │
│  hypertension_history: CharField ('yes'/'no')           │
│  smoking_history: CharField ('yes'/'no')                │
│  sedentary_minutes_day: IntegerField (0-1200)           │
│  screening_probability: FloatField (0.0-1.0)            │
│  ai_referral_recommended: BooleanField                  │
│  decision_threshold: DecimalField (0.1389)              │
│  model_sha256: CharField (64)                           │
│  preprocessor_sha256: CharField (64)                    │
└───────────────┬─────────────────────────┬───────────────┘
                │ 1:1                     │ 1:1
                ▼                         ▼
┌───────────────────────────────┐ ┌───────────────────────────────┐
│      ScreeningExplanation     │ │          HumanReview          │
│  id: UUID (PK)                │ │  id: UUID (PK)                │
│  screening_record_id: FK(1:1) │ │  screening_record_id: FK(1:1) │
│  status: 'generated'/'failed' │ │  reviewer_code: Char(32)      │
│  intercept: Float             │ │  review_action: 'accepted'    │
│  contributions_json: JSON     │ │                 'overridden'  │
│  reconstructed_prob: Float    │ │  final_referral_rec: Bool     │
│  reconstruction_error: Float  │ │  override_reason_code: Char   │
│  model_sha256: Char(64)       │ │  override_note: Text(500)     │
└───────────────────────────────┘ └───────────────┬───────────────┘
                                                  │ 1:1
                                                  ▼
                                  ┌───────────────────────────────┐
                                  │        Stage2Assessment       │
                                  │  id: UUID (PK)                │
                                  │  human_review_id: FK(1:1)     │
                                  │  hba1c_percent: Decimal(4,2)  │
                                  │  laboratory_range: Char       │
                                  │    ('normal_range',           │
                                  │     'prediabetes_range',      │
                                  │     'diabetes_range')         │
                                  │  range_rule_version: Char     │
                                  │  entry_method: 'manual'       │
                                  └───────────────────────────────┘
```

---

## 2. Integrity & Deletion Policies

- **Cascade Prevention:** `on_delete=models.PROTECT` is enforced on all domain relationships (`ScreeningExplanation.screening_record`, `HumanReview.screening_record`, `Stage2Assessment.human_review`). Records cannot be accidentally orphaned or deleted while downstream evidence exists.
- **Immutability:** Once written through the application workflows, records cannot be edited. Overrides create a new `HumanReview` audit entity linked to the immutable `ScreeningRecord`.

---

## 3. Clean Migration From Zero Verification

The entire migration sequence was executed against a brand new empty database file (`temp_reproducibility.sqlite3`):

1. Applied all core Django framework migrations (`contenttypes`, `auth`, `admin`, `sessions`).
2. Applied all predictor domain migrations in sequence:
   - `predictor.0001_initial`: Legacy schema baseline (preserved for non-destructive history)
   - `predictor.0002_screeningrecord`: Stage-1 intake domain model
   - `predictor.0003_screeningexplanation`: GAM-native XAI entity
   - `predictor.0004_humanreview`: Human review entity
   - `predictor.0005_humanreview_override_note_and_more`: Override taxonomy extension
   - `predictor.0006_stage2assessment`: Stage-2 confirmatory laboratory entity
3. **Execution Result:** Return code `0`. All 24 migrations applied cleanly.
4. **Django System Check:** `python manage.py check` reported: `System check identified no issues (0 silenced).`
