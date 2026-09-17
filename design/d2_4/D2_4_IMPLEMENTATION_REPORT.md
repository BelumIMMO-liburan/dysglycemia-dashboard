# Phase D2.4 Implementation Report: Screening Result Experience + Immutable Screening Record Persistence

**Phase:** D2.4  
**Status:** Complete  
**Date:** September 2026  
**Governing Skill:** `research-governance` (Highest Precedence)  
**Supporting Skills:** `dashboard-design`, `frontend-quality`  

---

## 1. Executive Summary

Phase D2.4 establishes the auditable persistence layer and primary user-facing result experience for Stage-1 non-laboratory dysglycemia screening. Connecting directly to the frozen Phase-5 GAM inference adapter (`screening_inference.py`), this phase successfully implements:

1. **Dedicated, Auditable Entity (`ScreeningRecord`):** Introduced a clean, privacy-preserving database entity using UUID primary keys, storing human-readable input semantics, full-precision screening probabilities, binary referral recommendations, locked decision threshold (`0.1389`), and model provenance SHA-256 checksums.
2. **Post-Redirect-Get (PRG) Architecture:** Form submission at `/screening/run/` executes inference, atomically creates the database record, and issues an HTTP 302 redirect to `/screening/<uuid:screening_id>/result/`.
3. **Zero Inference on Result Revisit:** Automated tests and manual verification confirm that viewing `/screening/<uuid:screening_id>/result/` **never reruns model inference**. The stored record is authoritative.
4. **Idempotency & Duplicate Submission Protection:** Protected by session-generated tokens preventing duplicate record creation or multiple inferences on double-clicks.
5. **Evidence-First Result UI:** Implemented clean primary result cards adhering strictly to research governance semantics:
   - Elevated Signal ($\ge 0.1389$): Restrained amber attention styling; *"Elevated screening signal"*; *"Referral for Stage-2 HbA1c assessment is recommended."*
   - Lower Signal ($< 0.1389$): Calm neutral styling; *"Lower screening signal"*; *"The screening model does not recommend referral for Stage-2 HbA1c assessment at the current research operating point."*; explicit caveat: *"A lower screening signal does not rule out dysglycemia."*
   - Restrained numerical probability callout without misleading 0–100% progress bars.
   - Collapsible input disclosures with units and research provenance metadata.
   - Persistent prominent research prototype disclaimers.
6. **Strict Scope Control:** Zero XAI/SHAP decompositions (deferred to D2.5); zero human override fields or review workflows (deferred to subsequent phases); and zero modification to frozen model artifacts.

---

## 2. Directory & Artifact Manifest

```
dashboard/
├── predictor/
│   ├── models.py                        # Added ScreeningRecord entity with UUID pk
│   ├── migrations/
│   │   └── 0002_screeningrecord.py     # Clean database migration
│   ├── views.py                         # Updated run_screening_view (PRG) & added screening_result_view
│   ├── urls.py                          # Added /screening/<uuid:screening_id>/result/ route
│   ├── templates/predictor/
│   │   ├── new_screening.html           # Added idempotency_token hidden field
│   │   └── screening_result.html        # Primary Stage-1 result screen template
│   └── tests.py                         # 34 passing unit, model, workflow & semantics tests
design/
└── d2_4/
    ├── D2_4_IMPLEMENTATION_REPORT.md    # This document
    ├── SCREENING_RECORD_PERSISTENCE_CONTRACT.md # Formal database schema & immutability contract
    ├── D2_4_RESULT_PRESENTATION_SPEC.md # Visual hierarchy, status tokens & prohibited language spec
    ├── D2_4_DATABASE_AUDIT.md           # Audit of legacy tables vs new entity
    ├── D2_4_ACCESSIBILITY_AUDIT.md      # WCAG 2.1 AA accessibility verification
    ├── D2_4_RESPONSIVE_AUDIT.md         # Multi-device breakpoint verification
    └── screenshots/
        ├── 01_elevated_result_desktop.png
        ├── 02_lower_result_desktop.png
        ├── 03_result_mobile.png
        ├── 04_screening_inputs_expanded.png
        └── 05_research_details_expanded.png
```

---

## 3. Database Model Audit Summary

Prior to creating migrations, an exhaustive audit of `dashboard/predictor/models.py` was conducted:

| Existing Model | Semantic Contents | Classification | Architectural Action |
| :--- | :--- | :--- | :--- |
| `Prediction` | Kaggle predictors (`HbA1c`, `glucose`, `heart_disease`), sequential integer ID, multi-model strings (`DLNN Baseline`), binary disease labels (`0 = Not Diabetic, 1 = Diabetic`), SHAP JSON. | **Class C: LEGACY — DO NOT USE** | Kept isolated for backward compatibility. Not reused or modified. |
| `Override` | Doctor names, binary disease prediction flips (`override_value: 0 or 1`), flagged feature JSON. | **Class C: LEGACY — DO NOT USE** | Kept isolated for backward compatibility. |
| **`ScreeningRecord`** (New) | UUIDv4 primary key, 7 locked Stage-1 predictors in human-readable semantics, 64-bit probability, boolean recommendation, locked threshold `0.1389`, model & preprocessor SHA-256 hashes, creation timestamp, idempotency token. | **APPROVED NEW ENTITY** | Created via migration `0002_screeningrecord.py`. |

---

## 4. Post-Redirect-Get Workflow & Idempotency

The screening execution sequence follows a strict Post-Redirect-Get design:

```
[ User Reviews Inputs ]
          │
          ▼
POST /screening/run/
  ├── 1. Server-side revalidation of Stage1ScreeningForm(request.POST)
  ├── 2. Check idempotency_token in database -> Redirect if existing
  ├── 3. Execute frozen inference via screening_inference.predict_screening()
  ├── 4. Open transaction.atomic():
  │       Create immutable ScreeningRecord
  │
  ▼
302 Redirect to /screening/<uuid:screening_id>/result/
          │
          ▼
GET /screening/<uuid:screening_id>/result/
  ├── Retrieve ScreeningRecord by UUID (404 if invalid)
  ├── NEVER calls model inference
  └── Render predictor/screening_result.html
```

### Idempotency Protection
A unique hex token (`idempotency_token`) is generated when the user enters the review state. If the user double-clicks or resubmits the form, the second POST detects the existing token in `ScreeningRecord` and issues a 302 redirect directly to the already-created record without recomputing GAM inference or persisting a duplicate row.

---

## 5. Automated Test Suite Results

The comprehensive test suite in `dashboard/predictor/tests.py` was executed:
```powershell
& 'C:\Users\Felix\AppData\Local\Programs\Python\Python310\python.exe' manage.py test predictor
```
```text
Creating test database for alias 'default'...
..................................
----------------------------------------------------------------------
Ran 34 tests in 0.300s

OK
Destroying test database for alias 'default'...
Found 34 test(s).
System check identified no issues (0 silenced).
```

### Key Verification Highlights:
- `test_valid_post_creates_screening_record_and_redirects`: Confirms 302 redirect to UUID result detail and zero legacy rows created.
- `test_result_detail_get_renders_without_rerunning_inference`: Mocks `predict_screening` and asserts `mock_predict.assert_not_called()` during GET.
- `test_duplicate_submission_protection`: Asserts second submission does not duplicate record or rerun model.
- `test_elevated_screening_signal_presentation`: Asserts amber attention badge and required referral wording.
- `test_lower_screening_signal_presentation`: Asserts neutral badge, non-diagnostic caveat, and absence of prohibited terms (*"normal"*, *"disease absent"*).

---

## 6. Protected Research Artifact Verification

SHA-256 cryptographic hashes for the protected research artifacts were confirmed byte-identical:

| File | Canonical SHA-256 Baseline | Post-Phase D2.4 SHA-256 | Status |
| :--- | :--- | :--- | :--- |
| `gam_final.pkl` | `204a94ff072ef4f1edecebf5a643738c006bbf010f3817b4bb798d3ea6fef41d` | `204a94ff072ef4f1edecebf5a643738c006bbf010f3817b4bb798d3ea6fef41d` | **BYTE IDENTICAL** |
| `preprocessor.pkl` | `6e56a01993a4a6971eb62c82699c49da6f31a3acec2a1169e07862409f42824d` | `6e56a01993a4a6971eb62c82699c49da6f31a3acec2a1169e07862409f42824d` | **BYTE IDENTICAL** |
| `FINAL_MODEL_SPECIFICATION_LOCKED.md` | `7d2a5eb9c349dabfca4f5387161c78833c8e996dc302e16955a4d588d68d9ec5` | `7d2a5eb9c349dabfca4f5387161c78833c8e996dc302e16955a4d588d68d9ec5` | **BYTE IDENTICAL** |
| `final_test_predictions.csv` | `fac969a00df57d6686c36b09e3de65858e2c744812e0ba3e8765b3f6165b5923` | `fac969a00df57d6686c36b09e3de65858e2c744812e0ba3e8765b3f6165b5923` | **BYTE IDENTICAL** |
